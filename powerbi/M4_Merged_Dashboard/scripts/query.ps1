param([int]$Port, [string]$QueryFile)

$dll = 'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.883.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll'
Add-Type -Path $dll

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Provider=MSOLAP;Data Source=localhost:$Port;")
$conn.Open()

$queries = (Get-Content -Raw $QueryFile) -split '(?m)^-----+\s*$'

foreach ($q in $queries) {
    $q = $q.Trim()
    if (-not $q) { continue }
    $label = ($q -split "`n")[0]
    Write-Output ("=" * 70)
    Write-Output $label
    try {
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = ($q -replace '(?m)^//.*$', '')
        $reader = $cmd.ExecuteReader()
        $cols = @()
        for ($i = 0; $i -lt $reader.FieldCount; $i++) { $cols += $reader.GetName($i) }
        $rows = @()
        while ($reader.Read()) {
            $o = New-Object psobject
            for ($i = 0; $i -lt $reader.FieldCount; $i++) {
                $name = $cols[$i] -replace '^\[|\]$', ''
                $val = $reader.GetValue($i)
                if ($val -is [double]) { $val = [math]::Round($val, 5) }
                $o | Add-Member -NotePropertyName $name -NotePropertyValue $val
            }
            $rows += $o
        }
        $reader.Close()
        if ($rows.Count -eq 1 -and $cols.Count -gt 3) {
            $rows[0].PSObject.Properties | ForEach-Object {
                Write-Output ("  {0,-34} {1}" -f $_.Name, $_.Value)
            }
        } else {
            $rows | Format-Table -AutoSize | Out-String -Width 200 | Write-Output
        }
    } catch {
        Write-Output ("  ERROR: " + $_.Exception.Message)
    }
}
$conn.Close()
