#!/bin/bash
virtualenv -p python3 venv
source venv/bin/activate
python3 check.py
if [ $? == 0 ]; then
    pip install -r requirements.txt
fi
cd appEscrime
flask loadbd
flask run -h 0.0.0.0 -p 8080
cd ../
deactivate