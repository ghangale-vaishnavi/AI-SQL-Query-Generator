🤖 AI SQL Query Generator

An AI-powered application that converts natural language questions into SQL queries using Generative AI. Users can generate, explain, fix, and execute SQL queries through an interactive Streamlit interface connected to MySQL databases.

🚀 Project Overview

AI SQL Query Generator helps users interact with databases without manually writing every SQL query. Simply enter a question in plain English, and the application generates the corresponding SQL query.

✨ Key Features

- Generate SQL: Convert natural language questions into SQL queries.
- Explain SQL: Understand SQL queries through AI-generated explanations.
- Fix SQL: Identify and correct SQL query errors.
- Execute SQL: Run SELECT queries and view database results.
- Database Explorer: Discover available databases, tables, and columns.
- Query History: Reuse previously generated queries.
- CSV Export: Download query results as CSV files.
- Dynamic Schema Detection: Generate queries based on the selected database structure.

🛠️ Technologies Used

- Python
- Streamlit
- MySQL
- Groq API
- Pandas
- Requests
- Python Dotenv
- MySQL Connector

🖥️ Application Modules

1. Generate SQL
2. Explain SQL
3. Fix SQL
4. Execute SQL
5. Database Explorer
6. Query History

⚙️ Installation and Setup

1. Clone the repository

git clone https://github.com/ghangale-vaishnavi/AI-SQL-Query-Generator.git

2. Open the project folder

cd AI-SQL-Query-Generator

3. Create a virtual environment

python -m venv venv

4. Activate the environment

Windows:

venv\Scripts\activate

5. Install dependencies

pip install -r requirements.txt

6. Configure environment variables

Create a ".env" file in the project folder:

GROQ_API_KEY=your_groq_api_key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password

Use your own API key and MySQL credentials. Never upload your ".env" file to GitHub.

7. Run the application

python -m streamlit run app.py

🗄️ Database

This project uses MySQL databases. The application can discover available databases and their tables and columns dynamically.

🎯 Project Objective

To simplify SQL learning and database interaction using Generative AI, while helping users generate, understand, debug, and execute SQL queries efficiently.

👩‍💻 Developed By

Vaishnavi Ghangale

Data Science Learner | Aspiring Data Analyst
