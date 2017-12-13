#https://eventlogxp.com/blog/exporting-event-logs-with-windows-powershell/
$now=get-date
$startdate=$now.adddays(-30)
$name = hostname
$el = get-eventlog -ComputerName $name -log Security -After $startdate -EntryType Error, Warning, Information, SuccessAudit, FailureAudit
$el |Select EntryType, TimeGenerated, Source, EventID, @{n='Message';e={$_.Message -replace '\s+', " "}} | Export-CSV eventlog.csv -NoTypeInfo