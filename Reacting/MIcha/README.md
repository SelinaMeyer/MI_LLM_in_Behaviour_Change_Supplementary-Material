# Chatbot_Gradio
 
Current branch:

"Postgres-DB-Integration"

To run on macOS:

1. brew install postgresql@13
2. brew services start postgresql@13
3. /usr/local/Cellar/postgresql@13/13.11_2/bin/createuser -s postgres

In pgadmin create new database `postgres`:
[[!Bildschirmfoto 2023-07-17 um 16.23.39.png]]

In IDE: 
Create virtual environment and install dependencies
1. pip3 install virtualenv (if not already installed)
2. virtualenv venv
3. source venv/bin/activate
4. pip install -r requirements.txt

python create_table.py

Then run app.py
There is a local and a shaerable link -> Share the shareable link with others for testing


important Evaluation-scripts:

Preprocessing_questionnaires_demographics.py

Hypthesis_Tests.ipynb

Classification_all_user_turns.ipynb