import re
import pandas as pd
import streamlit as st

from sql_generator import generate_sql, explain_sql, fix_sql
from database import (
    execute_query,
    get_databases,
    get_tables,
    get_table_schema
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AI SQL Query Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# DARK NAVY + PURPLE THEME
# ==================================================

st.markdown("""

<style>

/* MAIN APPLICATION */

.stApp {
    background: linear-gradient(
        135deg,
        #080d1b 0%,
        #11152b 55%,
        #17132e 100%
    );
    color: #f1f5f9;
}

[data-testid="stHeader"] {
    background: transparent;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}


/* SIDEBAR */

[data-testid="stSidebar"] {
    background: #0b1020 !important;
    border-right: 1px solid #29264b;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #cbd5e1;
}


/* HEADINGS */

h1, h2, h3, h4 {
    color: #f8fafc !important;
}


/* MAIN INTERFACE LABELS */

.stTextArea label,
.stTextInput label,
.stSelectbox label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p {
    color: #f1f5f9 !important;
    opacity: 1 !important;
}


/* HERO SECTION */

.hero {
    background: linear-gradient(
        120deg,
        #171d3b,
        #29204b
    );
    padding: 28px;
    border-radius: 18px;
    border: 1px solid #39345f;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 35px;
    margin-bottom: 10px;
}

.hero p {
    color: #cbd5e1;
    font-size: 15px;
}


/* METRIC CARDS */

.metric-card {
    background: #151b32;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #302d55;
    text-align: center;
}

.metric-card h2 {
    color: #a78bfa !important;
    font-size: 28px;
}

.metric-card p {
    color: #cbd5e1 !important;
    margin-bottom: 0;
}


/* BUTTONS */

.stButton > button {
    background: linear-gradient(
        90deg,
        #6d4aff,
        #9333ea
    ) !important;
    color: white !important;
    border: none !important;
    border-radius: 9px;
    padding: 9px 20px;
    font-weight: 600;
}

.stButton > button:hover {
    background: linear-gradient(
        90deg,
        #805fff,
        #a855f7
    ) !important;
    color: white !important;
}


/* DOWNLOAD BUTTONS */

.stDownloadButton > button {
    background: #252044 !important;
    color: white !important;
    border: 1px solid #805fff !important;
    border-radius: 9px;
}

.stDownloadButton > button:hover {
    background: #433078 !important;
    color: white !important;
}


/* TEXT INPUTS */

.stTextInput input,
.stTextArea textarea {
    background: #151b32 !important;
    color: #f1f5f9 !important;
    border: 1px solid #39345f !important;
    border-radius: 8px;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #94a3b8 !important;
}


/* DATABASE DROPDOWN */

/* Intentionally no custom dropdown styling.
   This preserves its existing Streamlit appearance. */


/* CUSTOM DARK STATUS BOX */

.dark-status {
    background: #151b32;
    border: 1px solid #51447a;
    border-radius: 10px;
    padding: 12px 14px;
    color: #cbd5e1;
    margin-top: 8px;
    margin-bottom: 12px;
}


/* CUSTOM EMPTY MESSAGE BOX */

.dark-empty {
    background: #151b32;
    border: 1px solid #39345f;
    border-radius: 10px;
    padding: 18px;
    color: #cbd5e1;
    margin-top: 10px;
}


/* DATABASE AND HISTORY EXPANDERS */

[data-testid="stExpander"] {
    background: #151b32 !important;
    border: 1px solid #39345f !important;
    border-radius: 10px !important;
    overflow: hidden;
}

[data-testid="stExpander"] details,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background: #151b32 !important;
    color: #f1f5f9 !important;
}

[data-testid="stExpander"] summary:hover {
    background: #252044 !important;
}


/* TABS */

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
}

.stTabs [data-baseweb="tab"] {
    background: #151b32;
    border-radius: 8px;
    color: #F1F5F9 !important;
    padding: 10px 18px;
}

.stTabs [aria-selected="true"] {
    background: #433078 !important;
    color: white !important;
}


/* METRICS */

[data-testid="stMetric"] {
    background: #151b32 !important;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #302d55;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
}


/* DATAFRAME */

[data-testid="stDataFrame"] {
    background: #151b32 !important;
    border: 1px solid #39345f;
    border-radius: 10px;
}


/* CODE BLOCKS */

[data-testid="stCodeBlock"] {
    background: #0b1020 !important;
    border: 1px solid #302d55;
    border-radius: 10px;
}


/* DIVIDERS */

hr {
    border-color: #302d55 !important;
}


/* FOOTER */

.footer {
    color: #94a3b8;
    text-align: center;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# SESSION STATE
# ==================================================

defaults = {
    "query_history": [],
    "sql_editor": "",
    "pending_reuse_query": None,
    "explanation": "",
    "fixed_sql": "",
    "generated_sql": "",
    "query_results": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# REUSE QUERY

if st.session_state.pending_reuse_query is not None:

    st.session_state.sql_editor = (
        st.session_state.pending_reuse_query
    )

    st.session_state.pending_reuse_query = None


# ==================================================
# DATABASE DISCOVERY
# ==================================================

available_databases = get_databases()

if not available_databases:

    st.markdown("""
    <div class="dark-empty">
        No databases found. Please check your MySQL connection
        and .env configuration.
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.markdown("## 🤖 AI SQL Studio")

    st.caption("Your intelligent SQL assistant")

    st.divider()

    # DATABASE EXPLORER

    st.markdown("### 🗄️ Database Explorer")

    default_index = (
        available_databases.index("company_db1")
        if "company_db1" in available_databases
        else 0
    )

    selected_database = st.selectbox(
        "Select Database",
        options=available_databases,
        index=default_index,
        key="selected_database"
    )

    st.markdown(
        f"""
        <div class="dark-status">
            🟢 Connected: <b>{selected_database}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # TABLE EXPLORER

    st.markdown("### 📂 Tables")

    database_tables = get_tables(selected_database)

    if database_tables:

        for table in database_tables:

            with st.expander(f"📋 {table}"):

                columns = get_table_schema(
                    selected_database,
                    table
                )

                if columns:

                    for column in columns:

                        st.markdown(
                            f"**{column['COLUMN_NAME']}**"
                        )

                        st.caption(
                            f"Type: {column['DATA_TYPE']} | "
                            f"Nullable: {column['IS_NULLABLE']} | "
                            f"Key: {column['COLUMN_KEY'] or 'None'}"
                        )

                else:

                    st.caption("No columns found.")

    else:

        st.markdown("""
        <div class="dark-empty">
            No tables found in this database.
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # TECHNOLOGY STACK

    st.markdown("### 🛠️ Technology Stack")

    st.caption("🐍 Python")
    st.caption("🧠 Groq AI")
    st.caption("🗄️ MySQL")
    st.caption("📊 Pandas")
    st.caption("⚡ Streamlit")


# ==================================================
# MAIN HEADER
# ==================================================

st.markdown("""
<div class="hero">
    <h1>🤖 AI SQL Query Generator</h1>
    <p>
        Generate, explain, fix and execute SQL queries
        using Artificial Intelligence.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    f"**Currently selected database:** `{selected_database}`"
)


# ==================================================
# DASHBOARD METRICS
# ==================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""
    <div class="metric-card">
        <h2>🤖 AI</h2>
        <p>Intelligent SQL Generation</p>
    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="metric-card">
        <h2>🗄️ MySQL</h2>
        <p>Database Integration</p>
    </div>
    """, unsafe_allow_html=True)

with col3:

    st.markdown(f"""
    <div class="metric-card">
        <h2>{len(st.session_state.query_history)}</h2>
        <p>Queries Generated</p>
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# SQL WORKSPACE
# ==================================================

st.write("")

st.markdown("## 💻 SQL Workspace")

tab1, tab2, tab3, tab4 = st.tabs([
    "✨ Generate SQL",
    "📖 Explain SQL",
    "🔧 Fix SQL",
    "▶️ Execute SQL"
])


# ==================================================
# TAB 1: GENERATE SQL
# ==================================================

with tab1:

    st.subheader("Generate SQL using AI")

    question = st.text_area(
        "Enter your question in simple English",
        placeholder="Example: Show all employees working in the IT department",
        height=110,
        key="question_input"
    )

    if st.button("✨ Generate SQL", key="generate_button"):

        if not question.strip():

            st.warning("Please enter a question.")

        else:

            with st.spinner("AI is generating your SQL query..."):

                generated_sql = generate_sql(
                    question,
                    database=selected_database
                )

            if (
                generated_sql.startswith("Error:")
                or generated_sql.startswith("AI API Error:")
            ):

                st.error(generated_sql)

            else:

                st.session_state.generated_sql = generated_sql

                st.session_state.sql_editor = generated_sql

                st.session_state.query_history.insert(
                    0,
                    {
                        "question": question,
                        "sql": generated_sql,
                        "database": selected_database
                    }
                )

    if st.session_state.generated_sql:

        st.success("SQL query generated successfully!")

        st.code(
            st.session_state.generated_sql,
            language="sql"
        )

        st.download_button(
            "⬇️ Download Generated SQL",
            data=st.session_state.generated_sql,
            file_name="generated_query.sql",
            mime="text/plain",
            key="download_generated_sql"
        )


# ==================================================
# TAB 2: EXPLAIN SQL
# ==================================================

with tab2:

    st.subheader("Understand your SQL query")

    explain_input = st.text_area(
        "Enter SQL query to explain",
        placeholder="SELECT * FROM employees;",
        height=130,
        key="explain_input"
    )

    if st.button("📖 Explain SQL", key="explain_button"):

        if not explain_input.strip():

            st.warning("Please enter an SQL query.")

        else:

            with st.spinner("AI is explaining your query..."):

                explanation = explain_sql(
                    explain_input,
                    database=selected_database
                )

            if (
                explanation.startswith("AI API Error:")
                or explanation.startswith("Error:")
            ):

                st.error(explanation)

            else:

                st.session_state.explanation = explanation

    if st.session_state.explanation:

        st.markdown("### 📝 SQL Explanation")

        st.markdown(st.session_state.explanation)


# ==================================================
# TAB 3: FIX SQL
# ==================================================

with tab3:

    st.subheader("Fix SQL errors using AI")

    fix_input = st.text_area(
        "Enter incorrect SQL query",
        placeholder="SELECT employee_name FROM employee;",
        height=120,
        key="fix_input"
    )

    error_message = st.text_area(
        "Enter SQL error message",
        placeholder="Example: Table does not exist",
        height=90,
        key="error_input"
    )

    if st.button("🔧 Fix SQL Query", key="fix_button"):

        if not fix_input.strip():

            st.warning("Please enter an SQL query.")

        elif not error_message.strip():

            st.warning("Please enter the SQL error message.")

        else:

            with st.spinner("AI is fixing your query..."):

                corrected_sql = fix_sql(
                    fix_input,
                    error_message,
                    database=selected_database
                )

            if (
                corrected_sql.startswith("AI API Error:")
                or corrected_sql.startswith("Error:")
            ):

                st.error(corrected_sql)

            else:

                st.session_state.fixed_sql = corrected_sql

    if st.session_state.fixed_sql:

        st.success("Corrected SQL query")

        st.code(
            st.session_state.fixed_sql,
            language="sql"
        )

        st.download_button(
            "⬇️ Download Fixed SQL",
            data=st.session_state.fixed_sql,
            file_name="fixed_query.sql",
            mime="text/plain",
            key="download_fixed_sql"
        )


# ==================================================
# TAB 4: EXECUTE SQL
# ==================================================

with tab4:

    st.subheader("Execute SQL Query")

    sql_query = st.text_area(
        "Enter SQL query",
        height=180,
        key="sql_editor",
        placeholder="SELECT * FROM employees;"
    )

    st.download_button(
        "⬇️ Download Current SQL",
        data=sql_query,
        file_name="my_query.sql",
        mime="text/plain",
        disabled=not sql_query.strip(),
        key="download_current_sql"
    )

    if st.button("▶️ Execute Query", key="execute_button"):

        if not sql_query.strip():

            st.warning("Please enter an SQL query.")

        else:

            cleaned_query = sql_query.strip()

            if not re.match(
                r"^\s*SELECT\b",
                cleaned_query,
                re.IGNORECASE
            ):

                st.error("Only SELECT queries are allowed.")

            elif ";" in cleaned_query.rstrip(";"):

                st.error("Multiple SQL statements are not allowed.")

            else:

                with st.spinner("Executing SQL query..."):

                    results = execute_query(
                        cleaned_query,
                        database=selected_database
                    )

                if results is None:

                    st.error("Query execution failed.")

                    st.session_state.query_results = None

                else:

                    st.session_state.query_results = pd.DataFrame(
                        results
                    )

    if st.session_state.query_results is not None:

        result_df = st.session_state.query_results

        if not result_df.empty:

            st.success("Query executed successfully!")

            st.dataframe(
                result_df,
                use_container_width=True
            )

            csv_data = result_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "⬇️ Download Results CSV",
                data=csv_data,
                file_name="sql_results.csv",
                mime="text/csv",
                key="download_results_csv"
            )

        else:

            st.info(
                "Query executed successfully, but no records were returned."
            )


# ==================================================
# QUERY HISTORY
# ==================================================

st.divider()

st.markdown("## 🕒 Query History")

if st.session_state.query_history:

    history_col1, history_col2 = st.columns([5, 1])

    with history_col1:

        st.caption("Your previously generated SQL queries")

    with history_col2:

        if st.button("🗑️ Clear History"):

            st.session_state.query_history = []

            st.rerun()

    for index, item in enumerate(
        st.session_state.query_history
    ):

        with st.expander(
            f"📋 Query {index + 1}: {item['question']}"
        ):

            st.caption(
                f"Database: {item['database']}"
            )

            st.code(
                item["sql"],
                language="sql"
            )

            history_col_a, history_col_b = st.columns(2)

            with history_col_a:

                if st.button(
                    "♻️ Reuse Query",
                    key=f"reuse_{index}"
                ):

                    st.session_state.pending_reuse_query = (
                        item["sql"]
                    )

                    st.rerun()

            with history_col_b:

                st.download_button(
                    "⬇️ Download SQL",
                    data=item["sql"],
                    file_name=f"query_{index + 1}.sql",
                    mime="text/plain",
                    key=f"history_download_{index}"
                )

else:

    st.markdown("""
    <div class="dark-empty">
        📝 No query history available yet.
        <br><br>
        Generate your first SQL query to see it here.
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.markdown("""
<div class="footer">
    AI SQL Query Generator |
    Built with Python, Streamlit, Groq AI and MySQL
</div>
""", unsafe_allow_html=True)