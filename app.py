import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------

st.set_page_config(
    page_title="Student Admission Dashboard",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Admission Dashboard")
st.markdown("---")

# ----------------------------------------------------
# FILE UPLOAD
# ----------------------------------------------------

st.subheader("📂 Upload CSV Files")

col1, col2 = st.columns(2)

with col1:
    admission_file = st.file_uploader(
        "Upload Admission CSV",
        type=["csv"]
    )

with col2:
    intake_file = st.file_uploader(
        "Upload Intake CSV",
        type=["csv"]
    )

if admission_file is None or intake_file is None:
    st.info("Please upload both CSV files to continue.")
    st.stop()

# ----------------------------------------------------
# LOAD DATA
# ----------------------------------------------------

try:

    students = pd.read_csv(admission_file)
    intake = pd.read_csv(intake_file)

except Exception as e:

    st.error(f"Unable to read CSV files.\n\n{e}")
    st.stop()

# ----------------------------------------------------
# CLEAN COLUMN NAMES
# ----------------------------------------------------

students.columns = students.columns.str.strip()
intake.columns = intake.columns.str.strip()

# ----------------------------------------------------
# CLEAN IMPORTANT COLUMNS
# ----------------------------------------------------

students["Branch"] = students["Branch"].astype(str).str.strip()

students["Reference"] = (
    students["Reference"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)

# ----------------------------------------------------
# DATE CONVERSION
# ----------------------------------------------------

students["Date of Joining"] = pd.to_datetime(

    students["Date of Joining"],

    format="mixed",

    errors="coerce"

)
# ----------------------------------------------------
# NUMERIC CONVERSION
# ----------------------------------------------------

if "Advance paid" in students.columns:

    students["Advance paid"] = pd.to_numeric(
        students["Advance paid"],
        errors="coerce"
    ).fillna(0)

# ----------------------------------------------------
# SEAT STATUS
# ----------------------------------------------------

filled = (
    students.groupby("Branch")
    .size()
    .reset_index(name="Filled")
)

seat_status = intake.merge(
    filled,
    on="Branch",
    how="left"
)

seat_status["Filled"] = (
    seat_status["Filled"]
    .fillna(0)
    .astype(int)
)

seat_status["Vacant"] = (
    seat_status["Total Intake"]
    - seat_status["Filled"]
)

seat_status["Vacant"] = seat_status["Vacant"].clip(lower=0)

seat_status["Percentage"] = (
    seat_status["Filled"]
    / seat_status["Total Intake"]
    * 100
).round(1)

# ----------------------------------------------------
# TODAY'S ADMISSIONS
# ----------------------------------------------------

today = pd.Timestamp.today().normalize()

today_count = len(

    students[
        students["Date of Joining"].dt.normalize()
        == today
    ]

)

# ----------------------------------------------------
# KPI CARDS
# ----------------------------------------------------

st.subheader("📊 Dashboard Summary")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    "Total Admissions",
    len(students)
)

k2.metric(
    "Total Intake",
    int(intake["Total Intake"].sum())
)

k3.metric(
    "Seats Filled",
    int(seat_status["Filled"].sum())
)

k4.metric(
    "Vacant Seats",
    int(seat_status["Vacant"].sum())
)

k5.metric(
    "Today's Admissions",
    today_count
)

st.markdown("---")
# ----------------------------------------------------
# DEPARTMENT SEAT STATUS
# ----------------------------------------------------

st.subheader("🏫 Department Seat Status")

# Prepare display table
display_status = seat_status[
    ["Branch", "Total Intake", "Filled", "Vacant", "Percentage"]
].copy()

display_status.columns = [
    "Department",
    "Intake",
    "Filled",
    "Vacant",
    "Filled %"
]

# ----------------------------------------------------
# Filled vs Vacant Seats (Stacked Horizontal Bar)
# ----------------------------------------------------

st.markdown("### 📊 Filled vs Vacant Seats")

bar_df = display_status.rename(
    columns={"Department": "Branch"}
)

fig_bar = px.bar(
    bar_df,
    y="Branch",
    x=["Filled", "Vacant"],
    orientation="h",
    title="Department-wise Filled and Vacant Seats",
    text_auto=True,
    color_discrete_sequence=["#87CEFA", "#1F4E79"]
)

fig_bar.update_layout(
    height=500,
    xaxis_title="Number of Seats",
    yaxis_title="Department",
    legend_title="Seat Status",
    barmode="stack"
)

st.plotly_chart(
    fig_bar,
    use_container_width=True
)

# ----------------------------------------------------
# Department Pie Chart
# ----------------------------------------------------

st.markdown("### 🥧 Department Occupancy")

selected_branch = st.selectbox(
    "Select Department",
    sorted(display_status["Department"].unique())
)

branch_data = display_status[
    display_status["Department"] == selected_branch
].iloc[0]

pie_df = pd.DataFrame({
    "Status": ["Filled", "Vacant"],
    "Seats": [
        branch_data["Filled"],
        branch_data["Vacant"]
    ]
})

fig_pie = px.pie(
    pie_df,
    names="Status",
    values="Seats",
    hole=0.45,
    title=f"{selected_branch} Seat Occupancy"
)

fig_pie.update_traces(
    textposition="inside",
    textinfo="percent+label+value"
)

st.plotly_chart(
    fig_pie,
    use_container_width=True
)

# ----------------------------------------------------
# Department Summary Table
# ----------------------------------------------------

st.markdown("### 📋 Department Summary")

st.dataframe(
    display_status,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")


# ----------------------------------------------------
# DAY-WISE ADMISSION TREND
# ----------------------------------------------------

st.subheader("📈 Day-wise Admission Trend")

trend = (
    students
    .dropna(subset=["Date of Joining"])
    .groupby(
        students["Date of Joining"].dt.date
    )
    .size()
    .reset_index(name="Admissions")
)

trend.columns = [
    "Date",
    "Admissions"
]

if len(trend) > 0:

    fig = px.line(
        trend,
        x="Date",
        y="Admissions",
        markers=True,
        title="Daily Admissions"
    )

    fig.update_layout(
        xaxis_title="Admission Date",
        yaxis_title="Number of Admissions",
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info("No admission dates available.")

st.markdown("---")

# ----------------------------------------------------
# FACULTY SEARCH
# ----------------------------------------------------

st.subheader("👨‍🏫 Faculty Search")

faculty_list = sorted(
    students["Reference"]
    .dropna()
    .astype(str)
    .unique()
)

selected_faculty = st.selectbox(
    "Search Faculty Reference",
    ["Select Faculty"] + faculty_list
)

if selected_faculty != "Select Faculty":

    faculty_students = students[
        students["Reference"] == selected_faculty
    ]

    st.success(
        f"Total Students Referred : {len(faculty_students)}"
    )

    st.dataframe(
        faculty_students,
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# ----------------------------------------------------
# STUDENT SEARCH
# ----------------------------------------------------

st.subheader("🔍 Student Search")

search = st.text_input(
    "Search by Student Name or Mobile Number"
)

if search:

    result = students[

        students["Name of the student"]
        .astype(str)
        .str.contains(
            search,
            case=False,
            na=False
        )

        |

        students["contact number 1"]
        .astype(str)
        .str.contains(
            search,
            case=False,
            na=False
        )

        |

        students["contact number 2"]
        .astype(str)
        .str.contains(
            search,
            case=False,
            na=False
        )

        |

        students["Branch"]
        .astype(str)
        .str.contains(
            search,
            case=False,
            na=False
        )

    ]

    st.success(f"{len(result)} record(s) found.")

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("Enter Student Name, Mobile Number or Branch.")

st.markdown("---")

# ----------------------------------------------------
# RECENT ADMISSIONS
# ----------------------------------------------------

st.subheader("🆕 Recent Admissions")

recent = students.sort_values(
    "Date of Joining",
    ascending=False
)

st.dataframe(
    recent.head(20),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# ----------------------------------------------------
# DOWNLOAD SECTION
# ----------------------------------------------------

st.subheader("📥 Download Reports")

col1, col2 = st.columns(2)

with col1:

    student_csv = students.to_csv(index=False).encode("utf-8")

    st.download_button(

        label="⬇ Download Admission Data",

        data=student_csv,

        file_name="Admission_Data.csv",

        mime="text/csv"

    )

with col2:

    seat_csv = display_status.to_csv(index=False).encode("utf-8")

    st.download_button(

        label="⬇ Download Seat Status",

        data=seat_csv,

        file_name="Seat_Status.csv",

        mime="text/csv"

    )

st.markdown("---")

# ----------------------------------------------------
# DASHBOARD INFORMATION
# ----------------------------------------------------

st.info(
    """
    📌 **Instructions**

    • Upload the latest Admission CSV and Intake CSV.

    • Dashboard updates automatically.

    • Faculty Search displays students referred by a faculty member.

    • Student Search works using Name, Mobile Number or Branch.

    • Recent Admissions always displays the latest 20 students.
    """
)

# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------

st.markdown("---")

st.caption(
    "🎓 Student Admission Dashboard | Developed using Streamlit by Dr. Srikanth Vemuri"
)
