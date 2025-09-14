Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Starting Streamlit application..." -ForegroundColor Green
Write-Host "Make sure to set your OPENAI_API_KEY in the .env file" -ForegroundColor Yellow
Write-Host ""

streamlit run streamlit_frontend.py
