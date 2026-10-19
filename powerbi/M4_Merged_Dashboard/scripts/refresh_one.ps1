param([int]$Port)

$dll = 'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.883.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll'
Add-Type -Path $dll

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Provider=MSOLAP;Data Source=localhost:$Port;")
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = 'SELECT [CATALOG_NAME] FROM $SYSTEM.DBSCHEMA_CATALOGS'
$r = $cmd.ExecuteReader(); $db = $null
while ($r.Read()) { $db = $r.GetValue(0) }
$r.Close()
Write-Output "database: $db"

$tables = @(
  'powerbi_model_summary',
  'powerbi_permutation_importance',
  'powerbi_dataset_inventory',
  'powerbi_threshold_curve',
  'powerbi_data_quality',
  'powerbi_households'
)

foreach ($t in $tables) {
    $tmsl = @"
{ "refresh": { "type": "full", "objects": [ { "database": "$db", "table": "$t" } ] } }
"@
    $c = $conn.CreateCommand()
    $c.CommandText = $tmsl
    try {
        $c.ExecuteNonQuery() | Out-Null
        # count the rows that actually landed
        $q = $conn.CreateCommand()
        $q.CommandText = "EVALUATE ROW(`"n`", COUNTROWS($t))"
        $rr = $q.ExecuteReader()
        $n = $null
        while ($rr.Read()) { $n = $rr.GetValue(0) }
        $rr.Close()
        Write-Output ("  OK    {0,-34} rows: {1}" -f $t, $n)
    } catch {
        $m = $_.Exception.Message -replace "`r?`n", ' | '
        if ($m.Length -gt 420) { $m = $m.Substring(0, 420) }
        Write-Output ("  FAIL  {0,-34} {1}" -f $t, $m)
    }
}
$conn.Close()
