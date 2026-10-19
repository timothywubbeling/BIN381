# Export the final report to PDF through Word, and audit the page budget while it is open.
#
#   powershell -ExecutionPolicy Bypass -File report\M4\export_pdf.ps1
#
# Run it from an ordinary PowerShell window. Word's automation server needs an
# interactive session: launched from a sandboxed or service-like context it blocks on a
# dialog nobody can see. If it hangs, close it, end any WINWORD.EXE left behind, and use
# Word itself: File > Save as > PDF, after letting it rebuild the contents page.
#
# Fields are updated, the document repaginated, and the fields updated again: the footer's
# "Page X of Y" counts pages, and rebuilding the contents page changes how many there are,
# so a single pass leaves the footer one page short.

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$doc = Join-Path $here 'BIN381_M4_Report_Group_P1.docx'
$pdf = Join-Path $here 'BIN381_M4_Report_Group_P1.pdf'
if (-not (Test-Path $doc)) { throw "$doc not found - run merge_final_report.py first" }

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    # read-only: nothing here changes the .docx, and an exclusive open can block on an
    # invisible 'file in use' prompt when Word is already running.
    $d = $word.Documents.Open($doc, $false, $true)
    foreach ($pass in 1, 2) {
        $d.Fields.Update() | Out-Null
        foreach ($toc in $d.TablesOfContents) { $toc.Update() | Out-Null }
        $d.Repaginate()
    }

    $pages = @{}
    foreach ($p in $d.Paragraphs) {
        $txt = ($p.Range.Text -replace '[\r\a]', '').Trim()
        if ($p.Style.NameLocal -like 'Heading 2*' -and $txt -and -not $pages.ContainsKey($txt)) {
            $pages[$txt] = $p.Range.Information(3)
        }
    }
    $start = $pages['Business problem and approach']
    $refs = $pages['References']
    $main = $refs - $start

    $d.ExportAsFixedFormat($pdf, 17)
    "wrote $pdf"
    "  pages        : $($d.ComputeStatistics(2)) in total"
    "  main content : $main page(s), sections 1 to 8 on pages $start to $($refs - 1)"
    if ($main -gt 10) {
        "  OVER THE LIMIT: the brief allows 10 pages of main content, excluding the cover," +
        " contents, references and appendices."
        exit 1
    }
    "  within the brief's 10-page limit (cover, contents, references and appendices excluded)"
    $d.Close(0)
} finally {
    $word.Quit()
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word)
}
