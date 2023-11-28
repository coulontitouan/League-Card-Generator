# Create a Python virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\Activate

# Run the check.py script
python check.py

# Check the exit code of check.py
if ($LASTEXITCODE -eq 0) {
    # Install Python dependencies from requirements.txt
    pip install -r requirements.txt
}

# Change directory to appEscrime
Set-Location -Path .\appEscrime

# Start the Flask application
flask run -h 0.0.0.0 -p 8080

exit