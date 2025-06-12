primero 
python3 -m venv .venv
source .venv/bin/activate
pip install pandas
pip install requests

uvicorn main:app --reload
