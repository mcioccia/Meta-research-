# AI-use disclosure: Prepared with OpenAI Codex assistance; verify before use.
# Educational purposes only. Not financial or investment advice.
$ErrorActionPreference = 'Stop'
Write-Output 'AI-use disclosure: Prepared with OpenAI Codex assistance.'
Write-Output 'Educational purposes only. Not financial or investment advice.'
$demoPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $demoPython)) {
    throw 'The Lab_14 Python environment is missing. See Lab_14_Prices_and_Streamlit.md.'
}
Push-Location -LiteralPath $PSScriptRoot
try {
    & $demoPython -m streamlit hello --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
}
finally {
    Pop-Location
}
