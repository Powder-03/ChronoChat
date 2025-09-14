@echo off
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting Streamlit application...
echo Make sure to set your OPENAI_API_KEY in the .env file
echo.

streamlit run streamlit_frontend.py
