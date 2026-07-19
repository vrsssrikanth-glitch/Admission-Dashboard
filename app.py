import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Student Admission Dashboard",
    layout="wide"
)

st.title("🎓 Student Admission Dashboard")

# Load Data
students = pd.read_csv("data/admissions.csv")
intake = pd.read_csv("data/intake.csv")

# Remove extra spaces
students.columns = students.columns.str.strip()
intake.columns = intake.columns.str.strip()

students["Branch"] = students["Branch"].str.strip()
students["Reference"] = students["Reference"].fillna("Unknown")

# -------------------------------
# Sidebar
# -------------------------------

st.sidebar.header("Filters")

branch = st.sidebar.multiselect(
    "Select Branch",
    students["Branch"].unique(),
    default=students["Branch"].unique()
)

reference = st.sidebar.multiselect(
    "Faculty Reference",
    students["Reference"].unique(),
    default=students["Reference"].unique()
)

filtered = students[
    students["Branch"].isin(branch) &
    students["Reference"].isin(reference)
]

# -------------------------------
# Dashboard Metrics
# -------------------------------

col1,col2,col3=st.columns(3)

col1.metric("Total Admissions",len(filtered))

col2.metric("Total Branches",filtered["Branch"].nunique())

col3.metric("Faculty References",filtered["Reference"].nunique())

st.divider()

# -------------------------------
# Seats Filled
# -------------------------------

filled = filtered.groupby("Branch").size().reset_index(name="Filled")

seat_status = intake.merge(filled,on="Branch",how="left")
seat_status["Filled"]=seat_status["Filled"].fillna(0)

seat_status["Vacant"]=seat_status["Total Intake"]-seat_status["Filled"]

seat_status["Percentage"]=(
seat_status["Filled"]/seat_status["Total Intake"]*100
).round(1)

st.subheader("Seat Status")

st.dataframe(seat_status,use_container_width=True)

fig=px.bar(
    seat_status,
    x="Branch",
    y=["Filled","Vacant"],
    barmode="stack",
    title="Filled vs Vacant Seats"
)

st.plotly_chart(fig,use_container_width=True)

# -------------------------------
# Faculty Reference
# -------------------------------

st.subheader("Faculty Reference Count")

ref=filtered.groupby("Reference").size().reset_index(name="Students")

fig2=px.pie(
    ref,
    names="Reference",
    values="Students",
    hole=0.45
)

st.plotly_chart(fig2,use_container_width=True)

# -------------------------------
# Branch Wise Admissions
# -------------------------------

st.subheader("Branch Wise Admissions")

fig3=px.bar(
    filtered.groupby("Branch").size().reset_index(name="Admissions"),
    x="Branch",
    y="Admissions",
    color="Admissions",
    text="Admissions"
)

st.plotly_chart(fig3,use_container_width=True)

# -------------------------------
# Search Student
# -------------------------------

st.subheader("Search Student")

search=st.text_input("Search by Name or Mobile")

if search:

    result=students[
        students["Name of the student"].str.contains(search,case=False,na=False)
        |
        students["contact number 1"].astype(str).str.contains(search)
        |
        students["contact number 2"].astype(str).str.contains(search)
    ]

    st.dataframe(result,use_container_width=True)

else:
    st.dataframe(filtered,use_container_width=True)