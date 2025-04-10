param (
    $InputPath="$PWD\RTS-GMLC-GIC-PNW.pwb",
    $GeoPath="$PWD\gic_east.csv",
    $BusSubPath="$PWD\RTS-GML-GIC_Bus-Sub-Mapping.csv",
    $OutputPath="$PWD\RTS-GMLC-GIC-East.pwb" 
)

Write-Output " In: $InputPath"
Write-Output "Geo: $GeoPath"
Write-Output "Sub: $BusSubPath"
Write-Output "Out: $OutputPath"
# Write-Output ''

If (Test-Path $OutputPath) {
    Remove-Item "$OutputPath" | Out-Null
}

function Test-SimAutoOutput {
    param (
        $Output,
        $ErrorMessage
    )

    $SimAutoError = $Output[0].Trim()

    If ($SimAutoError.Length -gt 0) {
        $SimAuto = $null

        If ($ErrorMessage -eq $null) {
            Throw "$SimAutoError"
        } Else {
            Throw "${ErrorMessage}. $SimAutoError"
        }
    }
    
    $Output[1]
}

function Invoke-SimAutoScript {
    param (
        $Instance,
        $Command,
        $ErrorMessage
    )

    Test-SimAutoOutput -Output $SimAuto.RunScriptCommand($Command) -ErrorMessage $ErrorMessage
}

$SimAuto = New-Object -ComObject pwrworld.SimulatorAuto
$SimAuto.CreateIfNotFound = $True
Test-SimAutoOutput -Output $SimAuto.OpenCase($InputPath) -ErrorMessage "There was an error opening ${InputPath}"
Invoke-SimAutoScript -Instance $SimAuto -Command 'EnterMode(EDIT)'

$Geo = Get-Content $GeoPath | ConvertFrom-Csv
$BusSubs = Get-Content $BusSubPath | Select-Object -Skip 1 | ConvertFrom-Csv

Write-Output ''
$BusLocations = @{}

foreach ($Bus in $Geo) {
    $BusNum = [Int] $Bus.'Bus ID'

    $BusLoc = @{}
    $BusLoc.X = [Double] $Bus.X
    $BusLoc.Y = [Double] $Bus.Y
    $x = $BusLoc.X
    $y = $BusLoc.Y
    $BusLocations[$BusNum] = $BusLoc
    Write-Output "Setting Location for bus $BusNum to ($x, $y)"
}

Write-Output ''
$SubLocations = @{}

foreach ($Bus in $BusSubs) {
    $BusNum = [Int] $Bus.Number
    $SubNum = [Int] $Bus.'Sub Num'
    $BusLoc = $BusLocations[$BusNum]
    if ($null -eq $BusLoc) { continue }
    $x = $BusLoc.X
    $y = $BusLoc.Y

    Write-Output "Changing location for sub $SubNum Associated with bus $BusNum to ($x, $y)"
    $SubLocations[$SubNum] = $BusLocations[$BusNum]
}

Write-Output ''

foreach ($SubNum in $SubLocations.Keys) {
    $SubLoc = $SubLocations[$SubNum]
    $x = $SubLoc.X
    $y = $SubLoc.Y

    $SubKeys = "Number", "Longitude", "Latitude"
    $SubVals = $SubNum, $SubLoc.X, $SubLoc.Y
    Write-Output "Setting location for substation $SubNum to ($x, $y)"
    Test-SimAutoOutput $SimAuto.ChangeParametersSingleElement("Substation", $SubKeys, $SubVals)
}

$Out = $SimAuto.SaveCase($OutputPath, "PWB21", $true) 
$Err = $Out[0]

If ($Err.Length -gt 0) {
    Write-Output "Error saving ${OutputPath}: $Err"
}

$SimAuto = $null
