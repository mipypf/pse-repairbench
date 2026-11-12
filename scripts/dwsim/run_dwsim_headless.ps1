param(
  [Parameter(Mandatory = $true)] [string] $InputPath,
  [string] $ZipEntryName = "",
  [string] $OutDir = ".tmp\dwsim_headless_run",
  [string] $ResultJsonPath = "",
  [int] $TimeoutSeconds = 90,
  [string] $DwsimDir = "$env:LOCALAPPDATA\DWSIM"
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

function ConvertTo-SafeName([string] $name) {
  $safe = $name -replace '[^\p{L}\p{Nd}\._-]+', '_'
  if ($safe.Length -gt 90) {
    return $safe.Substring(0, 90)
  }
  return $safe
}

function Resolve-FullPath([string] $path) {
  if ([System.IO.Path]::IsPathRooted($path)) {
    return $path
  }
  return Join-Path (Get-Location).Path $path
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
      throw "No .dwxmz or .dwxml entry found in $ZipPath."
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
$inputFullPath = Resolve-FullPath $InputPath
$outFullPath = Resolve-FullPath $OutDir
New-Item -ItemType Directory -Force -Path $outFullPath | Out-Null

if (!$ResultJsonPath) {
  $ResultJsonPath = Join-Path $outFullPath "result.json"
} else {
  $ResultJsonPath = Resolve-FullPath $ResultJsonPath
}

$stdout = Join-Path $outFullPath "worker.stdout.txt"
$stderr = Join-Path $outFullPath "worker.stderr.txt"
$workerResult = Join-Path $outFullPath "worker_result.json"
Remove-Item -LiteralPath $ResultJsonPath, $stdout, $stderr, $workerResult -ErrorAction SilentlyContinue

$inputExt = [System.IO.Path]::GetExtension($inputFullPath).ToLowerInvariant()
$simPath = $inputFullPath
$sourceEntry = ""

if ($inputExt -eq ".zip") {
  $safeBase = ConvertTo-SafeName ([System.IO.Path]::GetFileNameWithoutExtension($inputFullPath))
  $simPath = Join-Path $outFullPath ($safeBase + ".dwxmz")
  $sourceEntry = Extract-DwsimFile $inputFullPath $ZipEntryName $simPath
} elseif ($inputExt -notin @(".dwxmz", ".dwxml")) {
  throw "InputPath must be a .zip, .dwxmz, or .dwxml file."
}

$worker = Join-Path $root "scripts\dwsim\dwsim_headless_worker.ps1"
$started = Get-Date
$process = Invoke-WorkerProcess `
  -WorkerPath $worker `
  -DwsimDir $DwsimDir `
  -SimPath $simPath `
  -ResultJsonPath $workerResult `
  -StdoutPath $stdout `
  -StderrPath $stderr `
  -TimeoutSeconds $TimeoutSeconds `
  -WorkingDirectory $root

if (!$process.exited) {
  $result = [ordered]@{
    status = "timeout"
    input_path = $inputFullPath
    source_entry = $sourceEntry
    simulation_path = $simPath
    success = $false
    timeout_seconds = $TimeoutSeconds
    duration_sec = [math]::Round(((Get-Date) - $started).TotalSeconds, 3)
    worker_stdout = $stdout
    worker_stderr = $stderr
  }
} elseif (!(Test-Path -LiteralPath $workerResult)) {
  $result = [ordered]@{
    status = "worker_terminated"
    input_path = $inputFullPath
    source_entry = $sourceEntry
    simulation_path = $simPath
    success = $false
    exit_code = $process.exit_code
    duration_sec = [math]::Round(((Get-Date) - $started).TotalSeconds, 3)
    worker_stdout = $stdout
    worker_stderr = $stderr
  }
} else {
  $inner = Get-Content -LiteralPath $workerResult -Raw | ConvertFrom-Json
  $result = [ordered]@{
    status = $inner.status
    input_path = $inputFullPath
    source_entry = $sourceEntry
    simulation_path = $simPath
    success = [bool]($inner.status -eq "success" -and $inner.solved_after -eq $true -and $inner.exception_count -eq 0)
    solved_after = $inner.solved_after
    exception_count = $inner.exception_count
    exceptions = $inner.exceptions
    loaded_objects = $inner.loaded_objects
    error_message = $inner.error_message
    messages_log_count = $inner.messages_log_count
    dwsim_version = $inner.dwsim_version
    duration_sec = $inner.duration_sec
    worker_stdout = $stdout
    worker_stderr = $stderr
  }
}

$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ResultJsonPath -Encoding UTF8
$result | ConvertTo-Json -Depth 8

if ($result.success) {
  exit 0
}
exit 1
