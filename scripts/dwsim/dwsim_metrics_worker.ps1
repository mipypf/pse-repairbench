param(
  [Parameter(Mandatory = $true)] [string] $SimPath,
  [Parameter(Mandatory = $true)] [string] $ResultJsonPath,
  [string] $SavePath = "",
  [string] $ColumnGuid = "",
  [string] $DwsimDir = "$env:LOCALAPPDATA\DWSIM"
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Resolve-FullPath([string] $path) {
  if ([string]::IsNullOrWhiteSpace($path)) {
    return ""
  }
  if ([System.IO.Path]::IsPathRooted($path)) {
    return $path
  }
  return Join-Path (Get-Location).Path $path
}

$SimPath = Resolve-FullPath $SimPath
$ResultJsonPath = Resolve-FullPath $ResultJsonPath
if ($SavePath) {
  $SavePath = Resolve-FullPath $SavePath
}

function ConvertTo-NumberOrNull([string] $value) {
  if ([string]::IsNullOrWhiteSpace($value)) {
    return $null
  }
  if ($value -in @("NaN", "Infinity", "-Infinity")) {
    return $null
  }
  $parsed = 0.0
  if ([double]::TryParse(
      $value,
      [System.Globalization.NumberStyles]::Float,
      [System.Globalization.CultureInfo]::InvariantCulture,
      [ref] $parsed
    )) {
    return $parsed
  }
  return $null
}

function Get-ElementChildren($node, [string] $name = "") {
  $children = @()
  foreach ($child in $node.ChildNodes) {
    if ($child.NodeType -ne [System.Xml.XmlNodeType]::Element) {
      continue
    }
    if (!$name -or $child.Name -eq $name) {
      $children += $child
    }
  }
  return $children
}

function Get-FirstChild($node, [string] $name) {
  $children = @(Get-ElementChildren $node $name)
  if ($children.Count -eq 0) {
    return $null
  }
  return $children[0]
}

function Get-LastChild($node, [string] $name) {
  $children = @(Get-ElementChildren $node $name)
  if ($children.Count -eq 0) {
    return $null
  }
  return $children[$children.Count - 1]
}

function Get-ChildText($node, [string] $name) {
  $child = Get-FirstChild $node $name
  if ($null -eq $child) {
    return $null
  }
  return [string]$child.InnerText
}

function Get-StageNumberFromName([string] $stageName) {
  if ([string]::IsNullOrWhiteSpace($stageName)) {
    return $null
  }
  $match = [regex]::Match($stageName.Trim(), '^Stage_?(\d+)$')
  if ($match.Success) {
    return [int]$match.Groups[1].Value
  }
  return $null
}

function Read-DwsimXml([string] $path) {
  $extension = [System.IO.Path]::GetExtension($path).ToLowerInvariant()
  if ($extension -eq ".dwxml") {
    [xml]$document = Get-Content -LiteralPath $path -Raw
    return $document
  }
  if ($extension -ne ".dwxmz") {
    throw "Expected .dwxmz or .dwxml, got $path"
  }

  $archive = [System.IO.Compression.ZipFile]::OpenRead($path)
  try {
    $entry = $archive.Entries |
      Where-Object { $_.FullName -match '\.xml$' } |
      Sort-Object FullName |
      Select-Object -First 1
    if ($null -eq $entry) {
      throw "No XML entry found in $path"
    }
    $reader = New-Object System.IO.StreamReader($entry.Open())
    try {
      [xml]$document = $reader.ReadToEnd()
      return $document
    }
    finally {
      $reader.Dispose()
    }
  }
  finally {
    $archive.Dispose()
  }
}

function Get-GraphicTags($root) {
  $tags = @{}
  $graphicObjects = Get-FirstChild $root "GraphicObjects"
  if ($null -eq $graphicObjects) {
    return $tags
  }
  foreach ($graphic in @(Get-ElementChildren $graphicObjects)) {
    $name = Get-ChildText $graphic "Name"
    $tag = Get-ChildText $graphic "Tag"
    if (![string]::IsNullOrWhiteSpace($name)) {
      $tags[$name] = $tag
    }
  }
  return $tags
}

function Get-SimulationObjectTypes($root) {
  $types = @{}
  $simulationObjects = Get-FirstChild $root "SimulationObjects"
  if ($null -eq $simulationObjects) {
    return $types
  }
  foreach ($object in @(Get-ElementChildren $simulationObjects)) {
    $guid = Get-ChildText $object "Name"
    $type = Get-ChildText $object "Type"
    if (![string]::IsNullOrWhiteSpace($guid)) {
      $types[$guid] = $type
    }
  }
  return $types
}

function Test-IsMaterialStreamType([string] $type) {
  return (![string]::IsNullOrWhiteSpace($type) -and $type.Contains("MaterialStream") -and !$type.Contains("EnergyStream"))
}

function Test-IsUnitOperationType([string] $type) {
  return (![string]::IsNullOrWhiteSpace($type) -and !$type.Contains("MaterialStream") -and !$type.Contains("EnergyStream"))
}

function Get-ConnectorAttachedId($connector, [string] $direction) {
  if ($connector.GetAttribute("IsAttached").ToLowerInvariant() -ne "true") {
    return $null
  }
  if ($connector.GetAttribute("AttachedToEnergyConn").ToLowerInvariant() -eq "true") {
    return $null
  }
  if ($connector.GetAttribute("AttachedFromEnergyConn").ToLowerInvariant() -eq "true") {
    return $null
  }
  if ($direction -eq "upstream") {
    $value = $connector.GetAttribute("AttachedFromObjID")
  } else {
    $value = $connector.GetAttribute("AttachedToObjID")
  }
  if ([string]::IsNullOrWhiteSpace($value)) {
    return $null
  }
  return $value
}

function Parse-StreamGraph($root, $streams) {
  $tags = Get-GraphicTags $root
  $objectTypes = Get-SimulationObjectTypes $root
  $graphicObjects = Get-FirstChild $root "GraphicObjects"
  $flowById = @{}
  foreach ($stream in @($streams)) {
    if ($stream["id"]) {
      $flowById[$stream["id"]] = $stream
    }
  }
  $graphStreams = @()
  $terminal = @()
  if ($null -eq $graphicObjects) {
    return [ordered]@{
      streams = $graphStreams
      terminal_material_streams = $terminal
    }
  }

  foreach ($graphic in @(Get-ElementChildren $graphicObjects)) {
    $guid = Get-ChildText $graphic "Name"
    if ([string]::IsNullOrWhiteSpace($guid)) {
      continue
    }
    $type = if ($objectTypes.ContainsKey($guid)) { $objectTypes[$guid] } else { Get-ChildText $graphic "ObjectType" }
    if (!(Test-IsMaterialStreamType $type)) {
      continue
    }

    $upstream = @()
    $downstream = @()
    $inputConnectors = Get-FirstChild $graphic "InputConnectors"
    if ($null -ne $inputConnectors) {
      foreach ($connector in @(Get-ElementChildren $inputConnectors)) {
        $attached = Get-ConnectorAttachedId $connector "upstream"
        if ($attached -and $objectTypes.ContainsKey($attached) -and (Test-IsUnitOperationType $objectTypes[$attached])) {
          $upstream += $attached
        }
      }
    }
    $outputConnectors = Get-FirstChild $graphic "OutputConnectors"
    if ($null -ne $outputConnectors) {
      foreach ($connector in @(Get-ElementChildren $outputConnectors)) {
        $attached = Get-ConnectorAttachedId $connector "downstream"
        if ($attached -and $objectTypes.ContainsKey($attached) -and (Test-IsUnitOperationType $objectTypes[$attached])) {
          $downstream += $attached
        }
      }
    }

    $flow = if ($flowById.ContainsKey($guid)) { $flowById[$guid] } else { $null }
    $molarFlow = if ($null -ne $flow) { $flow["molar_flow"] } else { $null }
    $massFlow = if ($null -ne $flow) { $flow["mass_flow"] } else { $null }
    $nonzeroFlow = $false
    if (($null -ne $molarFlow -and [math]::Abs([double]$molarFlow) -gt 1e-12) -or
        ($null -ne $massFlow -and [math]::Abs([double]$massFlow) -gt 1e-12)) {
      $nonzeroFlow = $true
    }
    $isTerminal = ($upstream.Count -gt 0 -and $downstream.Count -eq 0)
    $item = [ordered]@{
      id = $guid
      tag = if ($tags.ContainsKey($guid)) { $tags[$guid] } else { $null }
      type = $type
      upstream_unit_guids = @($upstream | Sort-Object -Unique)
      downstream_unit_guids = @($downstream | Sort-Object -Unique)
      has_upstream_unit = ($upstream.Count -gt 0)
      has_downstream_unit = ($downstream.Count -gt 0)
      has_nonzero_flow = $nonzeroFlow
      is_terminal_material_stream = $isTerminal
      is_terminal_material_stream_with_flow = ($isTerminal -and $nonzeroFlow)
    }
    $graphStreams += $item
    if ($item.is_terminal_material_stream_with_flow) {
      $terminal += [ordered]@{
        id = $item.id
        tag = $item.tag
        upstream_unit_guids = $item.upstream_unit_guids
        molar_flow = $molarFlow
        mass_flow = $massFlow
      }
    }
  }

  return [ordered]@{
    streams = $graphStreams
    terminal_material_streams = $terminal
  }
}

function Parse-Column($root, [string] $targetGuid) {
  $simulationObjects = Get-FirstChild $root "SimulationObjects"
  if ($null -eq $simulationObjects) {
    return $null
  }

  $selected = $null
  foreach ($object in @(Get-ElementChildren $simulationObjects)) {
    $type = Get-ChildText $object "Type"
    if ($type -notmatch "DistillationColumn") {
      continue
    }
    $guid = Get-ChildText $object "Name"
    if (!$targetGuid -or $guid -eq $targetGuid) {
      $selected = $object
      break
    }
  }
  if ($null -eq $selected) {
    return $null
  }
  $guid = Get-ChildText $selected "Name"
  $tags = Get-GraphicTags $root

  $feedStage = [ordered]@{
    feed_stage = $null
    feed_stage_name = $null
    feed_stage_id = $null
    feed_stream_id = $null
  }
  $materialStreams = Get-FirstChild $selected "MaterialStreams"
  if ($null -ne $materialStreams) {
    $feedStreams = @()
    foreach ($stream in @(Get-ElementChildren $materialStreams)) {
      if ((Get-ChildText $stream "StreamBehavior") -eq "Feed") {
        $feedStreams += $stream
      }
    }
    if ($feedStreams.Count -eq 1) {
      $associatedStage = Get-ChildText $feedStreams[0] "AssociatedStage"
      $feedStage.feed_stream_id = Get-ChildText $feedStreams[0] "StreamID"
      $feedStage.feed_stage_id = $associatedStage
      $stages = Get-FirstChild $selected "Stages"
      if ($null -ne $stages) {
        foreach ($stage in @(Get-ElementChildren $stages)) {
          if ((Get-ChildText $stage "ID") -eq $associatedStage) {
            $stageName = Get-ChildText $stage "Name"
            $feedStage.feed_stage_name = $stageName
            $feedStage.feed_stage = Get-StageNumberFromName $stageName
            break
          }
        }
      }
    }
  }

  $specs = @()
  $specsNode = Get-FirstChild $selected "Specs"
  if ($null -ne $specsNode) {
    foreach ($spec in @(Get-ElementChildren $specsNode)) {
      $specs += [ordered]@{
        stype = Get-ChildText $spec "SType"
        spec_value = ConvertTo-NumberOrNull (Get-ChildText $spec "SpecValue")
        spec_unit = Get-ChildText $spec "SpecUnit"
        calculated_value = ConvertTo-NumberOrNull (Get-ChildText $spec "CalculatedValue")
        component_id = Get-ChildText $spec "ComponentID"
        stage_number = ConvertTo-NumberOrNull (Get-ChildText $spec "StageNumber")
      }
    }
  }

  [ordered]@{
    guid = $guid
    tag = if ($tags.ContainsKey($guid)) { $tags[$guid] } else { $null }
    type = Get-ChildText $selected "Type"
    reflux_ratio = ConvertTo-NumberOrNull (Get-ChildText $selected "RefluxRatio")
    number_of_stages = ConvertTo-NumberOrNull (Get-ChildText $selected "NumberOfStages")
    reboiler_duty = ConvertTo-NumberOrNull (Get-ChildText $selected "ReboilerDuty")
    condenser_duty = ConvertTo-NumberOrNull (Get-ChildText $selected "CondenserDuty")
    reboiler_pressure = ConvertTo-NumberOrNull (Get-ChildText $selected "ReboilerPressure")
    condenser_pressure = ConvertTo-NumberOrNull (Get-ChildText $selected "CondenserPressure")
    feed_stage = $feedStage.feed_stage
    feed_stage_name = $feedStage.feed_stage_name
    feed_stage_id = $feedStage.feed_stage_id
    feed_stream_id = $feedStage.feed_stream_id
    specs = $specs
  }
}

function Parse-TargetUnit($root, [string] $targetGuid) {
  if ([string]::IsNullOrWhiteSpace($targetGuid)) {
    return $null
  }
  $simulationObjects = Get-FirstChild $root "SimulationObjects"
  if ($null -eq $simulationObjects) {
    return $null
  }
  $tags = Get-GraphicTags $root
  foreach ($object in @(Get-ElementChildren $simulationObjects)) {
    $guid = Get-ChildText $object "Name"
    if ($guid -ne $targetGuid) {
      continue
    }
    $unitType = Get-ChildText $object "Type"
    return [ordered]@{
      guid = $guid
      tag = if ($tags.ContainsKey($guid)) { $tags[$guid] } else { $null }
      type = $unitType
      calc_mode = Get-ChildText $object "CalcMode"
      outlet_pressure = ConvertTo-NumberOrNull (Get-ChildText $object "OutletPressure")
      pout = ConvertTo-NumberOrNull (Get-ChildText $object "Pout")
      p_out = ConvertTo-NumberOrNull (Get-ChildText $object "POut")
      delta_p = ConvertTo-NumberOrNull (Get-ChildText $object "DeltaP")
      outlet_temperature = ConvertTo-NumberOrNull (Get-ChildText $object "OutletTemperature")
      override_p = Get-ChildText $object "OverrideP"
      override_t = Get-ChildText $object "OverrideT"
      flash_pressure = ConvertTo-NumberOrNull (Get-ChildText $object "FlashPressure")
      flash_temperature = ConvertTo-NumberOrNull (Get-ChildText $object "FlashTemperature")
    }
  }
  return $null
}

function Parse-Streams($root) {
  $tags = Get-GraphicTags $root
  $simulationObjects = Get-FirstChild $root "SimulationObjects"
  $streams = @()
  if ($null -eq $simulationObjects) {
    return $streams
  }

  foreach ($object in @(Get-ElementChildren $simulationObjects)) {
    $type = Get-ChildText $object "Type"
    if ($type -notmatch "MaterialStream") {
      continue
    }

    $id = Get-ChildText $object "Name"
    $phases = Get-FirstChild $object "Phases"
    $mixture = $null
    if ($null -ne $phases) {
      foreach ($phase in @(Get-ElementChildren $phases)) {
        if ((Get-ChildText $phase "ComponentName") -eq "Mixture") {
          $mixture = $phase
          break
        }
      }
      if ($null -eq $mixture) {
        $phaseChildren = @(Get-ElementChildren $phases)
        if ($phaseChildren.Count -gt 0) {
          $mixture = $phaseChildren[0]
        }
      }
    }

    $properties = $null
    $compounds = @{}
    if ($null -ne $mixture) {
      $properties = Get-LastChild $mixture "Properties"
      $compoundNode = $null
      foreach ($candidate in @(Get-ElementChildren $mixture "Compounds")) {
        if (@(Get-ElementChildren $candidate).Count -gt 0) {
          $compoundNode = $candidate
          break
        }
      }
      if ($null -ne $compoundNode) {
        foreach ($compound in @(Get-ElementChildren $compoundNode)) {
          $name = Get-ChildText $compound "ComponentName"
          if (![string]::IsNullOrWhiteSpace($name)) {
            $compounds[$name] = [ordered]@{
              mole_fraction = ConvertTo-NumberOrNull (Get-ChildText $compound "MoleFraction")
              mass_fraction = ConvertTo-NumberOrNull (Get-ChildText $compound "MassFraction")
              molar_flow = ConvertTo-NumberOrNull (Get-ChildText $compound "MolarFlow")
              mass_flow = ConvertTo-NumberOrNull (Get-ChildText $compound "MassFlow")
            }
          }
        }
      }
    }

    $streams += [ordered]@{
      id = $id
      tag = if ($tags.ContainsKey($id)) { $tags[$id] } else { $null }
      temperature = if ($null -ne $properties) { ConvertTo-NumberOrNull (Get-ChildText $properties "temperature") } else { $null }
      pressure = if ($null -ne $properties) { ConvertTo-NumberOrNull (Get-ChildText $properties "pressure") } else { $null }
      molar_flow = if ($null -ne $properties) { ConvertTo-NumberOrNull (Get-ChildText $properties "molarflow") } else { $null }
      mass_flow = if ($null -ne $properties) { ConvertTo-NumberOrNull (Get-ChildText $properties "massflow") } else { $null }
      total_energy_flow = ConvertTo-NumberOrNull (Get-ChildText $object "TotalEnergyFlow")
      compounds = $compounds
    }
  }

  return $streams
}

$started = Get-Date
$result = [ordered]@{
  status = "started"
  success = $false
  dwsim_version = $null
  simulation_path = $SimPath
  saved_flowsheet = if ($SavePath) { $SavePath } else { $null }
  loaded_objects = $null
  solved_before = $null
  solved_after = $null
  exception_count = $null
  exceptions = @()
  error_message = $null
  messages_log_count = $null
  duration_sec = $null
  column = $null
  target_unit = $null
  stream_graph = $null
  terminal_material_streams = @()
  streams = @()
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

  $metricsPath = $SimPath
  if ($SavePath) {
    $saveDir = [System.IO.Path]::GetDirectoryName($SavePath)
    if ($saveDir) {
      New-Item -ItemType Directory -Force -Path $saveDir | Out-Null
    }
    $automation.SaveFlowsheet($sim, $SavePath, $true)
    $metricsPath = $SavePath
  }

  $document = Read-DwsimXml $metricsPath
  $result.column = Parse-Column $document.DocumentElement $ColumnGuid
  $result.target_unit = Parse-TargetUnit $document.DocumentElement $ColumnGuid
  $result.streams = Parse-Streams $document.DocumentElement
  $result.stream_graph = Parse-StreamGraph $document.DocumentElement $result.streams
  $result.terminal_material_streams = $result.stream_graph["terminal_material_streams"]

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
  $result | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $ResultJsonPath -Encoding UTF8
}

if ($result.success) {
  exit 0
}
exit 1
