import os
import re
import requests
from dotenv import load_dotenv

from database import get_database_schema

load_dotenv()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "openai/gpt-oss-20b"


def ask_ai(prompt):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "Error: GROQ_API_KEY not found in .env file."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as error:
        return f"AI API Error: {error}"

    except (KeyError, IndexError, ValueError):
        return "Error: Unable to read the AI response."


def get_schema_context(database="company_db1"):
    schema = get_database_schema(database)

    if not schema:
        return f"No tables or schema found in database: {database}"

    schema_text = f"Database: {database}\n\n"

    for table_name, columns in schema.items():
        schema_text += f"Table: {table_name}\n"

        for column in columns:
            schema_text += (
                f"- {column['COLUMN_NAME']} "
                f"({column['DATA_TYPE']})"
            )

            if column["COLUMN_KEY"] == "PRI":
                schema_text += " PRIMARY KEY"

            if column["IS_NULLABLE"] == "NO":
                schema_text += " NOT NULL"

            schema_text += "\n"

        schema_text += "\n"

    return schema_text


def clean_sql_response(response):
    response = re.sub(r"```sql", "", response, flags=re.IGNORECASE)
    response = response.replace("```", "")
    return response.strip()


def generate_sql(question, database="company_db1"):
    schema = get_schema_context(database)

    prompt = f"""
You are an expert MySQL developer.

Database schema:
{schema}

User question:
{question}

Instructions:
1. Generate a valid MySQL query.
2. Use only tables and columns present in the schema.
3. Use JOIN only when appropriate.
4. Do not invent table or column names.
5. Generate SELECT queries only.
6. Return only the SQL query.
7. Do not include explanations or Markdown.

SQL Query:
"""

    response = ask_ai(prompt)
    return clean_sql_response(response)


def explain_sql(sql_query, database="company_db1"):
    schema = get_schema_context(database)

    prompt = f"""
You are an expert MySQL teacher.

Database schema:
{schema}

Explain this SQL query in simple beginner-friendly language.

SQL Query:
{sql_query}

Explain:
1. What the query does.
2. Which tables are used.
3. Which columns are used.
4. Explain WHERE, JOIN, GROUP BY, ORDER BY or other clauses if present.
5. Explain the expected output.

Use clear headings and bullet points.
"""

    return ask_ai(prompt)


def fix_sql(sql_query, error_message, database="company_db1"):
    schema = get_schema_context(database)

    prompt = f"""
You are an expert MySQL developer.

Database schema:
{schema}

SQL query with an error:
{sql_query}

Error message:
{error_message}

Instructions:
1. Identify and correct the SQL error.
2. Use only existing tables and columns from the schema.
3. Return a corrected SELECT query only.
4. Do not invent columns or tables.
5. Do not include explanations or Markdown.

Corrected SQL Query:
"""

    response = ask_ai(prompt)
    return clean_sql_response(response)