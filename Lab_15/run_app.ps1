# AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
# Educational purposes only. Not financial or investment advice.
Write-Output 'AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.'
Write-Output 'Educational purposes only. Not financial or investment advice.'
$lab15Python = Join-Path $PSScriptRoot '..\Lab_14\.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $lab15Python)) {
    $lab15Python = 'python'
}
Push-Location -LiteralPath $PSScriptRoot
try {
    & $lab15Python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502 --browser.gatherUsageStats false
} finally {
    Pop-Location
}
