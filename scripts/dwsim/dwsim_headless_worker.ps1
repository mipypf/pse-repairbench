param(
  [Parameter(Mandatory = $true)] [string] $DwsimDir,
  [Parameter(Mandatory = $true)] [string] $SimPath,
  [Parameter(Mandatory = $true)] [string] $ResultJsonPath
)

$ErrorActionPreference = "Stop"
$started = Get-Date
$result = [ordered]@{
  status = "started"
  dwsim_version = $null
  simulation_path = $SimPath
  loaded_objects = $null
  solved_before = $null
  solved_after = $null
  exception_count = $null
  success = $false
  exceptions = @()
  error_message = $null
  messages_log_count = $null
  duration_sec = $null
}

try {
  Set-Location -LiteralPath $DwsimDir
  $thermoCsDir = Join-Path $DwsimDir "ThermoCS"
  $thermoCsDll = Join-Path $thermoCsDir "ThermoCS.dll"
  if (Test-Path -LiteralPath $thermoCsDll) {
    $env:PATH = "$thermoCsDir;$env:PATH"
    [Reflection.Assembly]::LoadFrom($thermoCsDll) | Out-Null
  }
  foreach ($dll in @("CapeOpen.dll", "DWSIM.Interfaces.dll", "DWSIM.Automation.dll")) {
    [Reflection.Assembly]::LoadFrom((Join-Path $DwsimDir $dll)) | Out-Null
  }

  $automation = New-Object DWSIM.Automation.Automation3
  $result.dwsim_version = $automation.GetVersion()

  $sim = $automation.LoadFlowsheet($SimPath)
  $result.loaded_objects = $sim.SimulationObjects.Count
  $result.solved_before = [bool]$sim.Solved

  $exceptions = $automation.CalculateFlowsheet4($sim)
  if ($null -eq $exceptions) {
    $result.exception_count = 0
  } else {
    $result.exception_count = $exceptions.Count
    foreach ($ex in $exceptions) {
      $result.exceptions += [ordered]@{
        type = $ex.GetType().FullName
        message = $ex.Message
      }
    }
  }

  $result.solved_after = [bool]$sim.Solved
  $result.error_message = [string]$sim.ErrorMessage
  $result.messages_log_count = $sim.MessagesLog.Count
  if ($result.solved_after -and $result.exception_count -eq 0) {
    $result.status = "success"
    $result.success = $true
  } else {
    $result.status = "calculation_failed"
  }

  $automation.ReleaseResources()
}
catch {
  $result.status = "worker_error"
  $result.exceptions += [ordered]@{
    type = $_.Exception.GetType().FullName
    message = $_.Exception.Message
  }
}
finally {
  $result.duration_sec = [math]::Round(((Get-Date) - $started).TotalSeconds, 3)
  $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ResultJsonPath -Encoding UTF8
}

if ($result.success) {
  exit 0
}
exit 1
