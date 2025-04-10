$InputPath="$PWD\RTS-GMLC-GIC-PNW.pwb"
$GeoPath="$PWD\gic_north.csv"
$BusSubPath="$PWD\RTS-GML-GIC_Bus-Sub-Mapping.csv"
$OutputPath="$PWD\RTS-GMLC-GIC-North.pwb" 

.\Change-SubLocations.ps1 $InputPath $GeoPath $BusSubPath $OutputPath

