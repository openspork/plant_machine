Get-ChildItem -Recurse | Where-Object {$_.Name -match ".py|.html|.js"} | Get-Content | Measure-Object -Line -Word
