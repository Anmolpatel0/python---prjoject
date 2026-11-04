import streamlit as st
import pandas as pd
import json
import os

# File paths
CSV_FILE = 'students.csv'
JSON_FILE = 'students.json'

# --- 1. FUNCTIONS & FILE HANDLING WITH EXCEPTION HANDLING ---

def load_data():
    """Load student records from CSV safely."""
    if os.path.exists(CSV_FILE):
        try:
            return pd.read_csv(CSV_FILE)
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")
            return pd.DataFrame(columns=['ID', 'Name', 'Age', 'Grade', 'Course'])
    return pd.DataFrame(columns=['ID', 'Name', 'Age', 'Grade', 'Course'])

def save_data(df):
    """Save records simultaneously to both CSV and JSON formats."""
    try:
        # Save CSV
        df.to_csv(CSV_FILE, index=False)
        
        # Save JSON
        records = df.to_dict(orient='records')
        with open(JSON_FILE, 'w') as f:
            json.dump(records, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# Lambda Function example for formatting
format_name = lambda x: str(x).strip().title()

# --- 2. STREAMLIT APP LAYOUT & CONFIGURATION ---

st.set_page_config(
    page_title="Student Record Management System",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Record Management System")
st.markdown("A complete CRUD application built using Python, Streamlit, and CSV/JSON file handling.")

df = load_data()

# Navigation
menu = st.sidebar.radio("Navigation", ["View All Records", "Add Student", "Update Student", "Delete Student", "Analytics & Export"])

# --- 3. CRUD OPERATIONS ---

if menu == "View All Records":
    st.subheader("📋 Student Records")
    if not df.empty:
        search_query = st.text_input("🔍 Search Student by Name or Course").strip().lower()
        if search_query:
            # List comprehension filter logic
            filtered_df = df[
                df['Name'].astype(str).str.lower().str.contains(search_query) |
                df['Course'].astype(str).str.lower().str.contains(search_query)
            ]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
    else:
        st.info("No student records found. Add some students to get started!")

elif menu == "Add Student":
    st.subheader("➕ Add New Student")
    with st.form("add_student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.text_input("Student ID (Unique)")
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=1, max_value=100, step=1, value=18)
        with col2:
            grade = st.selectbox("Grade", ["A+", "A", "B+", "B", "C", "D", "F"])
            course = st.text_input("Course Name")
            
        submit_btn = st.form_submit_button("Submit")
        if submit_btn:
            try:
                if not student_id or not name or not course:
                    st.warning("Please fill out all required fields!")
                elif student_id in df['ID'].astype(str).values:
                    st.error("Student ID already exists! Please use a unique ID.")
                else:
                    cleaned_name = format_name(name)
                    new_record = pd.DataFrame([{
                        'ID': student_id,
                        'Name': cleaned_name,
                        'Age': int(age),
                        'Grade': grade,
                        'Course': course.strip()
                    }])
                    df = pd.concat([df, new_record], ignore_index=True)
                    if save_data(df):
                        st.success(f"Student '{cleaned_name}' added successfully!")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

elif menu == "Update Student":
    st.subheader("✏️ Update Student Record")
    if df.empty:
        st.info("No records available to update.")
    else:
        student_list = df['ID'].astype(str) + " - " + df['Name']
        selected_student = st.selectbox("Select Student to Update", student_list)
        selected_id = selected_student.split(" - ")[0]
        
        student_data = df[df['ID'].astype(str) == selected_id].iloc[0]
        
        with st.form("update_form"):
            col1, col2 = st.columns(2)
            with col1:
                updated_name = st.text_input("Full Name", value=student_data['Name'])
                updated_age = st.number_input("Age", min_value=1, max_value=100, value=int(student_data['Age']))
            with col2:
                grades = ["A+", "A", "B+", "B", "C", "D", "F"]
                grade_idx = grades.index(student_data['Grade']) if student_data['Grade'] in grades else 0
                updated_grade = st.selectbox("Grade", grades, index=grade_idx)
                updated_course = st.text_input("Course Name", value=student_data['Course'])
                
            update_btn = st.form_submit_button("Update Record")
            if update_btn:
                try:
                    df.loc[df['ID'].astype(str) == selected_id, ['Name', 'Age', 'Grade', 'Course']] = [
                        format_name(updated_name),
                        int(updated_age),
                        updated_grade,
                        updated_course.strip()
                    ]
                    if save_data(df):
                        st.success("Record updated successfully!")
                except Exception as e:
                    st.error(f"Failed to update record: {e}")

elif menu == "Delete Student":
    st.subheader("🗑️ Delete Student Record")
    if df.empty:
        st.info("No records available to delete.")
    else:
        student_list = df['ID'].astype(str) + " - " + df['Name']
        selected_student = st.selectbox("Select Student to Delete", student_list)
        selected_id = selected_student.split(" - ")[0]
        
        if st.button("Delete Permanently"):
            try:
                df = df[df['ID'].astype(str) != selected_id]
                if save_data(df):
                    st.success("Student record deleted successfully!")
            except Exception as e:
                st.error(f"Error during deletion: {e}")

elif menu == "Analytics & Export":
    st.subheader("📊 Data Summary & File Status")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students", len(df))
    col2.metric("Total Courses", len(df['Course'].unique()) if not df.empty else 0)
    col3.metric("Average Age", round(df['Age'].mean(), 1) if not df.empty else 0)
    
    st.markdown("---")
    st.subheader("📁 Data Files Status")
    st.write(f"**CSV Storage (`{CSV_FILE}`):** {'✅ Exists' if os.path.exists(CSV_FILE) else '❌ Not Found'}")
    st.write(f"**JSON Storage (`{JSON_FILE}`):** {'✅ Exists' if os.path.exists(JSON_FILE) else '❌ Not Found'}")
    
    if not df.empty:
        st.markdown("---")
        st.subheader("⬇️ Download Options")
        csv_data = df.to_csv(index=False).encode('utf-8')
        json_data = json.dumps(df.to_dict(orient='records'), indent=4)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button("Download CSV", csv_data, "student_records.csv", "text/csv")
        with col_b:
            st.download_button("Download JSON", json_data, "student_records.json", "application/json")
