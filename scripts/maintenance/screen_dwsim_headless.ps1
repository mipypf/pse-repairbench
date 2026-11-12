param(
  [int] $Limit = 0,
  [int] $Skip = 0,
  [int] $TimeoutSeconds = 90,
  [string] $RawDir = "raw_data\DWSIM_data",
  [string] $CatalogPath = "metadata\dwsim_sources\raw_data_catalog.csv",
  [string] $OutDir = ".tmp\raw_data_dwsim_screen",
  [string] $DwsimDir = "$env:LOCALAPPDATA\DWSIM",
  [string] $OnlyCategory = ""
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

function ConvertTo-SafeName([string] $name) {
  $safe = $name -replace '[^\p{L}\p{Nd}\._-]+', '_'
  if ($safe.Length -gt 80) {
    return $safe.Substring(0, 80)
  }
  return $safe
}

function Extract-DwsimFile([string] $ZipPath, [string] $EntryName, [string] $TargetPath) {
  $archive = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
  try {
    $entry = $null
    if ($EntryName) {
      $entry = $archive.Entries | Where-Object { $_.FullName -eq $EntryName } | Select-Object -First 1
    }
    if ($null -eq $entry) {
      $entry = $archive.Entries |
        Where-Object { $_.FullName -match '\.(dwxmz|dwxml)$' } |
        Sort-Object FullName |
        Select-Object -First 1
    }
    if ($null -eq $entry) {
      throw "No .dwxmz or .dwxml entry found."
    }
    $inStream = $entry.Open()
    try {
      $outStream = [System.IO.File]::Create($TargetPath)
      try {
        $inStream.CopyTo($outStream)
      }
      finally {
        $outStream.Dispose()
      }
    }
    finally {
      $inStream.Dispose()
    }
    return $entry.FullName
  }
  finally {
    $archive.Dispose()
  }
}

function New-Record($row, [string] $status, [string] $detail) {
  [ordered]@{
    zip_name = $row.zip_name
    dwsim_file_name = $row.dwsim_file_name
    estimated_category = $row.estimated_category
    scope_status = $row.scope_status
    category_confidence = $row.category_confidence
    catalog_object_count = $row.object_count
    result_status = $status
    success = $false
    solved_after = $null
    exception_count = $null
    exception_summary = $detail
    loaded_objects = $null
    duration_sec = $null
    worker_stdout = $null
    worker_stderr = $null
  }
}

function Invoke-WorkerProcess(
  [string] $WorkerPath,
  [string] $DwsimDir,
  [string] $SimPath,
  [string] $ResultJsonPath,
  [string] $StdoutPath,
  [string] $StderrPath,
  [int] $TimeoutSeconds,
  [string] $WorkingDirectory
) {
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = "powershell.exe"
  $psi.Arguments = ('-NoProfile -ExecutionPolicy Bypass -File "{0}" -DwsimDir "{1}" -SimPath "{2}" -ResultJsonPath "{3}"' -f $WorkerPath, $DwsimDir, $SimPath, $ResultJsonPath)
  $psi.WorkingDirectory = $WorkingDirectory
  $psi.UseShellExecute = $false
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.CreateNoWindow = $true

  $process = New-Object System.Diagnostics.Process
  $process.StartInfo = $psi
  $null = $process.Start()

  $stdoutTask = $process.StandardOutput.ReadToEndAsync()
  $stderrTask = $process.StandardError.ReadToEndAsync()
  $exited = $process.WaitForExit($TimeoutSeconds * 1000)

  if (!$exited) {
    try { $process.Kill() } catch {}
    try { $process.WaitForExit() } catch {}
  }

  Set-Content -LiteralPath $StdoutPath -Value $stdoutTask.Result -Encoding UTF8
  Set-Content -LiteralPath $StderrPath -Value $stderrTask.Result -Encoding UTF8

  [ordered]@{
    exited = $exited
    exit_code = if ($exited) { $process.ExitCode } else { $null }
  }
}

$root = (Get-Location).Path
$rawRoot = if ([System.IO.Path]::IsPathRooted($RawDir)) { $RawDir } else { Join-Path $root $RawDir }
$catalogFullPath = if ([System.IO.Path]::IsPathRooted($CatalogPath)) { $CatalogPath } else { Join-Path $root $CatalogPath }
$outRoot = if ([System.IO.Path]::IsPathRooted($OutDir)) { $OutDir } else { Join-Path $root $OutDir }
$worker = Join-Path $root "scripts\dwsim\dwsim_headless_worker.ps1"

New-Item -ItemType Directory -Force -Path $outRoot | Out-Null
$csvPath = Join-Path $outRoot "screen_results.csv"
$jsonlPath = Join-Path $outRoot "screen_results.jsonl"
Remove-Item -LiteralPath $csvPath, $jsonlPath -ErrorAction SilentlyContinue

$rows = Import-Csv -LiteralPath $catalogFullPath |
  Where-Object { $_.dwsim_file_count -eq "1" -and $_.read_status -like "readable*" }

if ($OnlyCategory) {
  $rows = $rows | Where-Object { $_.estimated_category -eq $OnlyCategory }
}
if ($Skip -gt 0) {
  $rows = $rows | Select-Object -Skip $Skip
}
if ($Limit -gt 0) {
  $rows = $rows | Select-Object -First $Limit
}

$records = New-Object System.Collections.Generic.List[object]
$index = 0
$total = @($rows).Count

foreach ($row in $rows) {
  $index += 1
  $zipPath = Join-Path $rawRoot $row.zip_name
  $safe = ConvertTo-SafeName ("{0:D4}_{1}" -f $index, [System.IO.Path]::GetFileNameWithoutExtension($row.zip_name))
  $caseDir = Join-Path $outRoot $safe
  New-Item -ItemType Directory -Force -Path $caseDir | Out-Null

  Write-Host ("[{0}/{1}] {2}" -f $index, $total, $row.zip_name)

  if (!(Test-Path -LiteralPath $zipPath)) {
    $record = New-Record $row "missing_zip" "zip file not found"
    $records.Add([pscustomobject]$record)
    continue
  }

  $suffix = if ($row.dwsim_file_suffix) { $row.dwsim_file_suffix.ToLowerInvariant() } else { "dwxmz" }
  $simPath = Join-Path $caseDir ("input." + $suffix)
  $resultJson = Join-Path $caseDir "worker_result.json"
  $stdout = Join-Path $caseDir "worker.stdout.txt"
  $stderr = Join-Path $caseDir "worker.stderr.txt"

  try {
    $null = Extract-DwsimFile $zipPath $row.dwsim_file_name $simPath
  }
  catch {
    $record = New-Record $row "extract_failed" $_.Exception.Message
    $records.Add([pscustomobject]$record)
    continue
  }

  Remove-Item -LiteralPath $resultJson, $stdout, $stderr -ErrorAction SilentlyContinue
  $started = Get-Date
  $process = Invoke-WorkerProcess `
    -WorkerPath $worker `
    -DwsimDir $DwsimDir `
    -SimPath $simPath `
    -ResultJsonPath $resultJson `
    -StdoutPath $stdout `
    -StderrPath $stderr `
    -TimeoutSeconds $TimeoutSeconds `
    -WorkingDirectory $root

  if (!$process.exited) {
    $record = New-Record $row "timeout" ("timeout after {0}s" -f $TimeoutSeconds)
    $record.duration_sec = [math]::Round(((Get-Date) - $started).TotalSeconds, 3)
    $record.worker_stdout = $stdout
    $record.worker_stderr = $stderr
    $records.Add([pscustomobject]$record)
  }
  elseif (!(Test-Path -LiteralPath $resultJson)) {
    $record = New-Record $row "worker_terminated" ("exit_code={0}; no result JSON" -f $process.exit_code)
    $record.duration_sec = [math]::Round(((Get-Date) - $started).TotalSeconds, 3)
    $record.worker_stdout = $stdout
    $record.worker_stderr = $stderr
    $records.Add([pscustomobject]$record)
  }
  else {
    $workerResult = Get-Content -LiteralPath $resultJson -Raw | ConvertFrom-Json
    $record = New-Record $row $workerResult.status ""
    $record.success = [bool]($workerResult.status -eq "success" -and $workerResult.solved_after -eq $true -and $workerResult.exception_count -eq 0)
    $record.solved_after = $workerResult.solved_after
    $record.exception_count = $workerResult.exception_count
    $record.loaded_objects = $workerResult.loaded_objects
    $record.duration_sec = $workerResult.duration_sec
    $record.worker_stdout = $stdout
    $record.worker_stderr = $stderr
    if ($workerResult.exceptions -and $workerResult.exceptions.Count -gt 0) {
      $first = @($workerResult.exceptions)[0]
      $record.exception_summary = ("{0}: {1}" -f $first.type, $first.message)
    }
    $records.Add([pscustomobject]$record)
  }

  $records | Export-Csv -LiteralPath $csvPath -NoTypeInformation -Encoding UTF8
  $records | ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 8 } | Set-Content -LiteralPath $jsonlPath -Encoding UTF8
}

$records | Export-Csv -LiteralPath $csvPath -NoTypeInformation -Encoding UTF8
$records | ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 8 } | Set-Content -LiteralPath $jsonlPath -Encoding UTF8

$successes = @($records | Where-Object { $_.success -eq $true })
Write-Host ("Done. screened={0} success={1} csv={2}" -f $records.Count, $successes.Count, $csvPath)
