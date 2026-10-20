import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ---------------- DATABASE ----------------

conn = sqlite3.connect("students.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE,
    name TEXT NOT NULL,
    semester TEXT,
    mathematics REAL,
    python REAL,
    dbms REAL,
    os_marks REAL,
    ai_marks REAL,
    attendance REAL
)
""")

conn.commit()

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Student Performance Evaluation System",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Performance Evaluation System")
st.write(
    "A Python-based application for evaluating and "
    "analyzing student academic performance."
)

# ---------------- HELPER FUNCTIONS ----------------

def calculate_percentage(row):
    subjects = [
        row["mathematics"],
        row["python"],
        row["dbms"],
        row["os_marks"],
        row["ai_marks"]
    ]

    return sum(subjects) / 5


def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"


def load_students():
    df = pd.read_sql_query(
        "SELECT * FROM students ORDER BY id DESC",
        conn
    )

    if not df.empty:
        df["percentage"] = df.apply(
            calculate_percentage, axis=1
        )

        df["grade"] = df["percentage"].apply(
            calculate_grade
        )

    return df


# ---------------- SIDEBAR ----------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a page",
    [
        "Dashboard",
        "Add Student",
        "Student Records",
        "Performance Analysis"
    ]
)

# ---------------- ADD STUDENT ----------------

if page == "Add Student":

    st.header("Register Student")

    with st.form("student_form"):

        student_id = st.text_input("Student ID")
        name = st.text_input("Student Name")
        semester = st.selectbox(
            "Semester",
            ["1", "2", "3", "4", "5", "6", "7", "8"]
        )

        st.subheader("Subject Marks (Out of 100)")

        col1, col2 = st.columns(2)

        with col1:
            mathematics = st.number_input(
                "Mathematics", 0.0, 100.0, 0.0
            )

            python_marks = st.number_input(
                "Python Programming", 0.0, 100.0, 0.0
            )

            dbms = st.number_input(
                "DBMS", 0.0, 100.0, 0.0
            )

        with col2:
            os_marks = st.number_input(
                "Operating Systems", 0.0, 100.0, 0.0
            )

            ai_marks = st.number_input(
                "Artificial Intelligence", 0.0, 100.0, 0.0
            )

            attendance = st.number_input(
                "Attendance Percentage",
                0.0,
                100.0,
                75.0
            )

        submitted = st.form_submit_button(
            "Save Student Record"
        )

        if submitted:

            if not student_id.strip() or not name.strip():
                st.error(
                    "Please enter both Student ID and Name."
                )

            else:
                try:
                    conn.execute(
                        """
                        INSERT INTO students (
                            student_id, name, semester,
                            mathematics, python, dbms,
                            os_marks, ai_marks, attendance
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            student_id.strip(),
                            name.strip(),
                            semester,
                            mathematics,
                            python_marks,
                            dbms,
                            os_marks,
                            ai_marks,
                            attendance
                        )
                    )

                    conn.commit()

                    st.success(
                        "Student record saved successfully!"
                    )

                except sqlite3.IntegrityError:
                    st.error(
                        "This Student ID already exists."
                    )


# ---------------- DASHBOARD ----------------

elif page == "Dashboard":

    st.header("Academic Dashboard")

    df = load_students()

    if df.empty:
        st.info(
            "No student records available. "
            "Add students to view the dashboard."
        )

    else:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Students",
            len(df)
        )

        col2.metric(
            "Average Percentage",
            f"{df['percentage'].mean():.2f}%"
        )

        col3.metric(
            "Highest Percentage",
            f"{df['percentage'].max():.2f}%"
        )

        col4.metric(
            "Average Attendance",
            f"{df['attendance'].mean():.2f}%"
        )

        st.subheader("Student Performance")

        st.dataframe(
            df[
                [
                    "student_id",
                    "name",
                    "semester",
                    "percentage",
                    "grade",
                    "attendance"
                ]
            ],
            use_container_width=True
        )


# ---------------- STUDENT RECORDS ----------------

elif page == "Student Records":

    st.header("Student Records")

    df = load_students()

    if df.empty:
        st.info("No records found.")

    else:
        search = st.text_input(
            "Search by Student ID or Name"
        )

        if search:
            df = df[
                df["student_id"].astype(str).str.contains(
                    search, case=False, na=False
                )
                |
                df["name"].astype(str).str.contains(
                    search, case=False, na=False
                )
            ]

        st.dataframe(
            df,
            use_container_width=True
        )

        csv_data = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Student Records CSV",
            data=csv_data,
            file_name="student_performance.csv",
            mime="text/csv"
        )


# ---------------- PERFORMANCE ANALYSIS ----------------

elif page == "Performance Analysis":

    st.header("Performance Analysis")

    df = load_students()

    if df.empty:
        st.info(
            "Add student records to generate charts."
        )

    else:
        st.subheader("Percentage Comparison")

        fig1, ax1 = plt.subplots()

        ax1.bar(
            df["name"],
            df["percentage"]
        )

        ax1.set_xlabel("Student Name")
        ax1.set_ylabel("Percentage")
        ax1.set_title("Student Performance Comparison")

        ax1.tick_params(
            axis="x",
            rotation=45
        )

        fig1.tight_layout()

        st.pyplot(fig1)
        plt.close(fig1)

        st.subheader("Grade Distribution")

        grade_counts = (
            df["grade"]
            .value_counts()
            .reindex(
                ["A+", "A", "B", "C", "D", "F"],
                fill_value=0
            )
        )

        fig2, ax2 = plt.subplots()

        ax2.bar(
            grade_counts.index,
            grade_counts.values
        )

        ax2.set_xlabel("Grade")
        ax2.set_ylabel("Number of Students")
        ax2.set_title("Grade Distribution")

        st.pyplot(fig2)
        plt.close(fig2)

        st.subheader("Subject-wise Class Average")

        subject_columns = [
            "mathematics",
            "python",
            "dbms",
            "os_marks",
            "ai_marks"
        ]

        subject_names = [
            "Mathematics",
            "Python",
            "DBMS",
            "Operating Systems",
            "AI"
        ]

        averages = df[subject_columns].mean()

        fig3, ax3 = plt.subplots()

        ax3.bar(
            subject_names,
            averages.values
        )

        ax3.set_ylabel("Average Marks")
        ax3.set_title("Subject-wise Average Marks")

        ax3.tick_params(
            axis="x",
            rotation=25
        )

        fig3.tight_layout()

        st.pyplot(fig3)
        plt.close(fig3)

# ---------------- FOOTER ----------------

st.sidebar.markdown("---")
st.sidebar.caption(
    "Student Performance Evaluation System | Python Mini Project"
)