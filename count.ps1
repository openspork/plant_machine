$results = Get-ChildItem -Recurse | Where-Object {$_.Name -match ".py|.html|.js" -and $_.Name -notmatch '__pycache_'} | Get-Content | Measure-Object -Line -Word

Write-Host $results

PAUSE