param([int]$Port)

$dll = 'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.883.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll'
Add-Type -Path $dll

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Provider=MSOLAP;Data Source=localhost:$Port;")
$conn.Open()

# which database is loaded in this workspace?
$cmd = $conn.CreateCommand()
$cmd.CommandText = 'SELECT [CATALOG_NAME] FROM $SYSTEM.DBSCHEMA_CATALOGS'
$reader = $cmd.ExecuteReader()
$db = $null
while ($reader.Read()) { $db = $reader.GetValue(0) }
$reader.Close()
Write-Output "database: $db"

# partition state before
$cmd = $conn.CreateCommand()
$cmd.CommandText = 'SELECT [TABLE_NAME], [REFRESHED_TIME] FROM $SYSTEM.TMSCHEMA_PARTITIONS'
try {
    $reader = $cmd.ExecuteReader()
    while ($reader.Read()) {
        Write-Output ("  before: {0,-34} {1}" -f $reader.GetValue(0), $reader.GetValue(1))
    }
    $reader.Close()
} catch { Write-Output ("  (partition state unavailable: " + $_.Exception.Message + ")") }

Write-Output "`nrefreshing ..."
$tmsl = @"
{
  "refresh": {
    "type": "full",
    "objects": [ { "database": "$db" } ]
  }
}
"@
$cmd = $conn.CreateCommand()
$cmd.CommandText = $tmsl
try {
    $cmd.ExecuteNonQuery() | Out-Null
    Write-Output "refresh completed"
} catch {
    Write-Output ("REFRESH ERROR: " + $_.Exception.Message)
}

$cmd = $conn.CreateCommand()
$cmd.CommandText = 'SELECT [TABLE_NAME], [REFRESHED_TIME] FROM $SYSTEM.TMSCHEMA_PARTITIONS'
try {
    $reader = $cmd.ExecuteReader()
    while ($reader.Read()) {
        Write-Output ("  after:  {0,-34} {1}" -f $reader.GetValue(0), $reader.GetValue(1))
    }
    $reader.Close()
} catch { Write-Output ("  (partition state unavailable)") }

$conn.Close()
