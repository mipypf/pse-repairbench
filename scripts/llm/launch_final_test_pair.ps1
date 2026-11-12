param(
  [Parameter(Mandatory = $true)] [ValidateSet("anthropic", "gemini", "openai")] [string] $ProviderA,
  [Parameter(Mandatory = $true)] [string] $ModelA,
  [Parameter(Mandatory = $true)] [ValidateSet("anthropic", "gemini", "openai")] [string] $ProviderB,
  [Parameter(Mandatory = $true)] [string] $ModelB,
  [ValidateSet("dev", "test")] [string] $Split = "dev",
  [string] $PromptMode = "parameter-selection",
  [string] $RunLabel = "",
  [string] $DatasetSplitId = "",
  [int] $ExecutorTimeoutSec = 60,
  [int] $DwsimTimeoutSec = 180,
  [double] $ProviderCallDelaySecA = 0.0,
  [double] $ProviderCallDelaySecB = 0.0,
  [switch] $DryRunSanitize,
  [switch] $Wait
)

$ErrorActionPreference = "Stop"

function Quote-PsString([string] $Value) {
  return "'" + $Value.Replace("'", "''") + "'"
}

function Model-Slug([string] $Model) {
  return ($Model -replace "[^A-Za-z0-9._-]", "_")
}

function Write-ChildScript(
  [string] $Root,
  [string] $Python,
  [string] $Provider,
  [string] $Model,
  [string] $PromptMode,
  [string] $DatasetSplitId,
  [int] $ExecutorTimeoutSec,
  [int] $DwsimTimeoutSec,
  [double] $ProviderCallDelaySec,
  [string[]] $InstancePaths,
  [string] $RunDir,
  [bool] $DryRun
) {
  $scriptPath = Join-Path $RunDir "run_model.ps1"
  $stdout = Join-Path $RunDir "run_stdout.log"
  $stderr = Join-Path $RunDir "run_stderr.log"
  $pathLines = ($InstancePaths | ForEach-Object { "  " + (Quote-PsString $_) }) -join ",`n"
  $dryRunLine = if ($DryRun) { "  '--dry-run-sanitize'," } else { "" }
  $content = @"
`$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $(Quote-PsString $Root)
`$python = $(Quote-PsString $Python)
`$stdout = $(Quote-PsString $stdout)
`$stderr = $(Quote-PsString $stderr)
`$paths = @(
$pathLines
)
`$cmdArgs = @(
  'scripts\llm\run_llm_pilot_batch.py',
  '--provider', $(Quote-PsString $Provider),
  '--model', $(Quote-PsString $Model),
  '--prompt-mode', $(Quote-PsString $PromptMode),
  '--work-dir', $(Quote-PsString $RunDir),
  '--dataset-split-id', $(Quote-PsString $DatasetSplitId),
  '--executor-timeout-sec', $(Quote-PsString ([string] $ExecutorTimeoutSec)),
  '--dwsim-timeout-sec', $(Quote-PsString ([string] $DwsimTimeoutSec)),
  '--provider-call-delay-sec', $(Quote-PsString ([string] $ProviderCallDelaySec)),
$dryRunLine
  '--instances'
) + `$paths
& `$python @cmdArgs 1> `$stdout 2> `$stderr
exit `$LASTEXITCODE
"@
  Set-Content -LiteralPath $scriptPath -Value $content -Encoding UTF8
  return $scriptPath
}

$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
  throw "Python executable not found: $python"
}

if (-not $RunLabel) {
  $RunLabel = Get-Date -Format "yyyyMMdd_HHmmss"
}
if (-not $DatasetSplitId) {
  $DatasetSplitId = "final_v0_1_5_$Split"
}

$splitFile = Join-Path $root "instances\final_v0_1_5\splits\$Split.txt"
if (-not (Test-Path -LiteralPath $splitFile)) {
  throw "Split file not found: $splitFile"
}

$ids = Get-Content -LiteralPath $splitFile | Where-Object { $_ }
$paths = foreach ($id in $ids) {
  Join-Path $root (Join-Path "instances\final_v0_1_5\candidate_pool" $id)
}

$jobs = @(
  @{ Provider = $ProviderA; Model = $ModelA; ProviderCallDelaySec = $ProviderCallDelaySecA },
  @{ Provider = $ProviderB; Model = $ModelB; ProviderCallDelaySec = $ProviderCallDelaySecB }
)

$launched = @()
foreach ($job in $jobs) {
  $slug = Model-Slug $job.Model
  $runDir = Join-Path $root (Join-Path "results\final_v0_1_5\$Split\$slug\$PromptMode" "run_$RunLabel")
  if (Test-Path -LiteralPath (Join-Path $runDir "aggregate.json")) {
    throw "Refusing to overwrite existing aggregate: $(Join-Path $runDir 'aggregate.json')"
  }
  New-Item -ItemType Directory -Force -Path $runDir | Out-Null

  $launcherInfo = [ordered]@{
    provider = $job.Provider
    model = $job.Model
    prompt_mode = $PromptMode
    dataset_split_id = $DatasetSplitId
    split = $Split
    instance_count = $paths.Count
    executor_timeout_sec = $ExecutorTimeoutSec
    dwsim_timeout_sec = $DwsimTimeoutSec
    provider_call_delay_sec = $job.ProviderCallDelaySec
    dry_run_sanitize = [bool] $DryRunSanitize
    started_at = (Get-Date).ToString("o")
  }
  $launcherInfo | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $runDir "launcher_info.json") -Encoding UTF8

  $childScript = Write-ChildScript `
    -Root $root `
    -Python $python `
    -Provider $job.Provider `
    -Model $job.Model `
    -PromptMode $PromptMode `
    -DatasetSplitId $DatasetSplitId `
    -ExecutorTimeoutSec $ExecutorTimeoutSec `
    -DwsimTimeoutSec $DwsimTimeoutSec `
    -ProviderCallDelaySec $job.ProviderCallDelaySec `
    -InstancePaths $paths `
    -RunDir $runDir `
    -DryRun ([bool] $DryRunSanitize)

  $process = Start-Process `
    -FilePath "powershell" `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $childScript) `
    -PassThru `
    -WindowStyle Hidden

  $launched += [ordered]@{
    provider = $job.Provider
    model = $job.Model
    pid = $process.Id
    run_dir = $runDir
    child_script = $childScript
  }
}

$launched | ConvertTo-Json -Depth 6

if ($Wait) {
  foreach ($item in $launched) {
    $runningProcess = Get-Process -Id $item.pid -ErrorAction SilentlyContinue
    if ($runningProcess) {
      Wait-Process -Id $item.pid
    }
  }
  foreach ($item in $launched) {
    $aggregate = Join-Path $item.run_dir "aggregate.json"
    if (Test-Path -LiteralPath $aggregate) {
      Write-Output "DONE $($item.provider)/$($item.model): $aggregate"
    } else {
      Write-Output "MISSING_AGGREGATE $($item.provider)/$($item.model): $($item.run_dir)"
    }
  }
}
