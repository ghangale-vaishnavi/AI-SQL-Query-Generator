import streamlit as st
import pandas as pd

from sql_generator import generate_sql, explain_sql, fix_sql
from database import execute_query


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI SQL Query Generator",
    page_icon="🤖",
    layout="wide"
)


# ==========================================
# 2. INITIALIZE SESSION STATE
# ==========================================

if "query_history" not in st.session_state:
    st.session_state["query_history"] = []

if "query_results" not in st.session_state:
    st.session_state["query_results"] = None

if "sql_query" not in st.session_state:
    st.session_state["sql_query"] = ""

if "query_to_execute" not in st.session_state:
    st.session_state["query_to_execute"] = ""

# Load a reused query before creating its text area
if "pending_reuse_query" in st.session_state:
    st.session_state["query_to_execute"] = (
        st.session_state.pop("pending_reuse_query")
    )


# ==========================================
# 3. APPLICATION HEADING
# ==========================================

st.title("🤖 AI SQL Query Generator")

st.write(
    "Generate, explain, fix and execute MySQL queries using AI."
)

if "reuse_message" in st.session_state:
    st.success(st.session_state.pop("reuse_message"))

st.divider()


# ==========================================
# 4. GENERATE SQL
# ==========================================

st.subheader("1. Generate SQL Query")

question = st.text_area(
    "Enter your question:",
    placeholder="Example: Show all employees earning more than 30000",
    height=100
)

if st.button("Generate SQL", type="primary"):

    if question.strip():

        with st.spinner("AI is generating your SQL query..."):

            try:

                result = generate_sql(question)

                st.session_state["sql_query"] = result
                st.session_state["query_to_execute"] = result

                st.session_state["current_question"] = question

                st.session_state["query_results"] = None

                st.session_state.pop("sql_explanation", None)
                st.session_state.pop("fixed_sql", None)

                # Save query in history
                st.session_state["query_history"].insert(
                    0,
                    {
                        "question": question,
                        "sql": result
                    }
                )

                st.success("SQL generated successfully!")

            except Exception as error:
                st.error(f"Generation Error: {error}")

    else:

        st.warning("Please enter a question.")


# ==========================================
# 5. DISPLAY GENERATED SQL
# ==========================================

if st.session_state["sql_query"]:

    sql_query = st.session_state["sql_query"]

    st.divider()

    st.subheader("2. Generated SQL Query")

    st.code(sql_query, language="sql")

    st.caption(
        "To copy the SQL, select the code and press Ctrl + C."
    )


    # ======================================
    # 6. EXPLAIN SQL
    # ======================================

    if st.button("Explain SQL"):

        with st.spinner("AI is explaining your query..."):

            try:

                explanation = explain_sql(sql_query)

                st.session_state["sql_explanation"] = explanation

            except Exception as error:

                st.error(f"Explanation Error: {error}")


    if "sql_explanation" in st.session_state:

        st.subheader("SQL Explanation")

        st.markdown(
            st.session_state["sql_explanation"]
        )


    # ======================================
    # 7. FIX SQL
    # ======================================

    st.divider()

    st.subheader("3. Fix SQL Query")

    incorrect_query = st.text_area(
        "Enter your incorrect SQL query:",
        value=sql_query,
        height=100,
        key="incorrect_query"
    )

    error_message = st.text_area(
        "Enter your MySQL error message:",
        placeholder="Example: Unknown column 'salary'",
        key="error_message"
    )

    if st.button("Fix SQL Query"):

        if incorrect_query.strip() and error_message.strip():

            with st.spinner("AI is fixing your SQL query..."):

                try:

                    fixed_result = fix_sql(
                        incorrect_query,
                        error_message
                    )

                    st.session_state["fixed_sql"] = fixed_result

                except Exception as error:

                    st.error(f"Fix Error: {error}")

        else:

            st.warning(
                "Please enter both the SQL query and error message."
            )


    if "fixed_sql" in st.session_state:

        st.subheader("Corrected SQL and Explanation")

        st.markdown(
            st.session_state["fixed_sql"]
        )


    # ======================================
    # 8. EXECUTE SQL
    # ======================================

    st.divider()

    st.subheader("4. Execute SQL Query")

    st.info("Only SELECT queries are allowed.")

    query_to_execute = st.text_area(
        "SQL query to execute:",
        height=120,
        key="query_to_execute"
    )

    if st.button("Run SQL Query", type="primary"):

        cleaned_query = query_to_execute.strip()

        # Basic SELECT-only validation
        if not cleaned_query:

            st.warning("Please enter a SQL query.")

        elif not cleaned_query.upper().startswith("SELECT"):

            st.error("Only SELECT queries are allowed.")

        elif ";" in cleaned_query.rstrip(";"):

            st.error("Multiple SQL statements are not allowed.")

        else:

            with st.spinner("Executing query in MySQL..."):

                try:

                    results = execute_query(cleaned_query)

                    if results is not None:

                        st.session_state["query_results"] = results

                        if results:

                            st.success(
                                "Query executed successfully!"
                            )

                        else:

                            st.info(
                                "Query executed successfully. No records found."
                            )

                except Exception as error:

                    st.error(f"Execution Error: {error}")


    # ======================================
    # 9. DISPLAY RESULTS
    # ======================================

    if st.session_state["query_results"] is not None:

        results = st.session_state["query_results"]

        st.divider()

        st.subheader("5. Query Results")

        if results:

            dataframe = pd.DataFrame(results)

            st.dataframe(
                dataframe,
                use_container_width=True
            )

            st.success(
                f"Total Records: {len(dataframe)}"
            )

            csv_data = dataframe.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="Download Results as CSV",
                data=csv_data,
                file_name="sql_query_results.csv",
                mime="text/csv"
            )

        else:

            st.info("No records available to display.")


# ==========================================
# 10. QUERY HISTORY
# ==========================================

st.divider()

st.subheader("6. Query History")

history = st.session_state["query_history"]

if history:

    st.write(
        f"Total saved queries: {len(history)}"
    )

    if st.button("Clear Query History"):

        st.session_state["query_history"] = []

        st.success("Query history cleared!")

        st.rerun()


    for index, item in enumerate(history):

        with st.expander(
            f"Query {index + 1}: {item['question']}"
        ):

            st.write("Original Question:")

            st.write(item["question"])

            st.write("Generated SQL:")

            st.code(
                item["sql"],
                language="sql"
            )

            if st.button(
                "Reuse This Query",
                key=f"reuse_{index}"
            ):

                # Store query for the next application run
                st.session_state["pending_reuse_query"] = item["sql"]

                st.session_state["sql_query"] = item["sql"]

                st.session_state["current_question"] = item["question"]

                st.session_state["query_results"] = None

                st.session_state.pop("sql_explanation", None)
                st.session_state.pop("fixed_sql", None)

                st.session_state["reuse_message"] = (
                    "Previous query loaded successfully!"
                )

                st.rerun()

else:

    st.info(
        "No query history available yet. Generate your first SQL query!"
    )