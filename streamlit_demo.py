"""Streamlit Demo for Patient Management System

This is a simple web UI that connects to the FastAPI backend running on
http://localhost:8000. Make sure to start the FastAPI server first:

    uvicorn main:app --reload --port 8000

Then run this Streamlit app:

    streamlit run streamlit_demo.py
"""

import streamlit as st
import requests
import json
from typing import Dict, Any, List


# Configuration
API_BASE_URL = "http://127.0.0.1:8002"


def get_all_patients() -> Dict[str, Any]:
    """Fetch all patients from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/view")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching patients: {e}")
        return {}


def get_patient_by_id(patient_id: str) -> Dict[str, Any]:
    """Fetch a specific patient by ID."""
    try:
        response = requests.get(f"{API_BASE_URL}/patient/{patient_id}")
        if response.status_code == 404:
            st.error("Patient not found")
            return {}
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.error("Patient not found")
        return {}


def create_patient(patient_data: Dict[str, Any]) -> bool:
    """Create a new patient."""
    try:
        with st.spinner(f"Creating patient {patient_data.get('id', 'Unknown')}..."):
            response = requests.post(f"{API_BASE_URL}/create/", json=patient_data)
            
            if response.status_code == 201:
                st.success(f"✅ Patient {patient_data.get('id')} created successfully!")
                return True
            elif response.status_code == 400:
                error_detail = response.json().get('detail', 'Bad request')
                st.error(f"❌ Failed to create patient: {error_detail}")
                return False
            else:
                st.error(f"❌ Unexpected response: {response.status_code} - {response.text}")
                return False
                
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to FastAPI server. Is it running on port 8002?")
        return False
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. Please try again.")
        return False
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return False


def update_patient(patient_id: str, update_data: Dict[str, Any]) -> bool:
    """Update an existing patient."""
    try:
        response = requests.put(f"{API_BASE_URL}/edit/{patient_id}", json=update_data)
        response.raise_for_status()
        st.success(f"✅ Patient {patient_id} updated successfully!")
        st.info("📋 Updated patient data:")
        st.json(update_data)
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating patient: {e}")
        return False


def delete_patient(patient_id: str) -> bool:
    """Delete a patient."""
    try:
        response = requests.delete(f"{API_BASE_URL}/delete/{patient_id}")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting patient: {e}")
        return False


def sort_patients(sort_by: str, order: str) -> List[Dict[str, Any]]:
    """Sort patients by a field."""
    try:
        response = requests.get(f"{API_BASE_URL}/sort/", params={"sort_by": sort_by, "order": order})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error sorting patients: {e}")
        return []


def main():
    st.set_page_config(
        page_title="Patient Management System",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 Patient Management System")
    st.markdown("A demo interface for the FastAPI Patient Management backend")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["View All Patients", "Search Patient", "Create Patient", "Update Patient", "Delete Patient", "Sort Patients"]
    )
    
    if page == "View All Patients":
        st.header("📋 All Patients")
        
        if st.button("Refresh Data"):
            st.rerun()
        
        patients = get_all_patients()
        if patients:
            # Convert to list for table display
            patient_list = []
            for patient_id, patient_data in patients.items():
                patient_record = {"ID": patient_id, **patient_data}
                # Calculate BMI if height and weight are available
                if "height" in patient_data and "weight" in patient_data:
                    bmi = round(patient_data["weight"] / (patient_data["height"] ** 2), 2)
                    patient_record["BMI"] = bmi
                patient_list.append(patient_record)
            
            st.dataframe(patient_list, use_container_width=True)
            st.info(f"Total patients: {len(patient_list)}")
        else:
            st.warning("No patients found or unable to connect to API")
    
    elif page == "Search Patient":
        st.header("🔍 Search Patient")
        
        patient_id = st.text_input("Enter Patient ID (e.g., P001):")
        
        if st.button("Search"):
            if patient_id:
                patient = get_patient_by_id(patient_id)
                if patient:
                    st.success(f"Patient {patient_id} found!")
                    
                    # Display patient info in a nice format
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Basic Information")
                        st.write(f"**Name:** {patient.get('name', 'N/A')}")
                        st.write(f"**Age:** {patient.get('age', 'N/A')}")
                        st.write(f"**Gender:** {patient.get('gender', 'N/A')}")
                        st.write(f"**City:** {patient.get('city', 'N/A')}")
                    
                    with col2:
                        st.subheader("Health Metrics")
                        st.write(f"**Height:** {patient.get('height', 'N/A')} m")
                        st.write(f"**Weight:** {patient.get('weight', 'N/A')} kg")
                        
                        # Calculate and display BMI
                        if "height" in patient and "weight" in patient:
                            bmi = round(patient["weight"] / (patient["height"] ** 2), 2)
                            st.write(f"**BMI:** {bmi}")
                            
                            # BMI verdict
                            if bmi < 18.5:
                                verdict = "Underweight"
                                color = "blue"
                            elif 18.5 <= bmi < 24.9:
                                verdict = "Normal weight"
                                color = "green"
                            elif 25 <= bmi < 29.9:
                                verdict = "Overweight"
                                color = "orange"
                            else:
                                verdict = "Obesity"
                                color = "red"
                            
                            st.markdown(f"**Verdict:** :{color}[{verdict}]")
                else:
                    st.error("Patient not found")
            else:
                st.warning("Please enter a Patient ID")
    
    elif page == "Create Patient":
        st.header("➕ Create New Patient")
        
        with st.form("create_patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                patient_id = st.text_input("Patient ID*", placeholder="P001")
                name = st.text_input("Full Name*", placeholder="John Doe")
                age = st.number_input("Age*", min_value=1, max_value=120, value=30)
                gender = st.selectbox("Gender*", ["male", "female", "others"])
            
            with col2:
                city = st.text_input("City*", placeholder="New York")
                height = st.number_input("Height (meters)*", min_value=0.5, max_value=3.0, value=1.75, step=0.01)
                weight = st.number_input("Weight (kg)*", min_value=10.0, max_value=500.0, value=70.0, step=0.1)
            
            submitted = st.form_submit_button("Create Patient")
            
            if submitted:
                # Show what data will be sent
                st.info("🔍 Validating patient data...")
                
                if all([patient_id, name, city, age, gender, height, weight]):
                    patient_data = {
                        "id": patient_id,
                        "name": name,
                        "city": city,
                        "age": age,
                        "gender": gender,
                        "height": height,
                        "weight": weight
                    }
                    
                    # Show a preview of the data being sent
                    st.write("📋 Patient data to be created:")
                    st.json(patient_data)
                    
                    if create_patient(patient_data):
                        st.info("🔄 You can now view the patient in 'View All Patients' or search by ID")
                else:
                    st.error("❌ Please fill in all required fields marked with *")
    
    elif page == "Update Patient":
        st.header("✏️ Update Patient")
        
        patient_id = st.text_input("Enter Patient ID to update:")
        
        if patient_id and st.button("Load Patient Data"):
            patient = get_patient_by_id(patient_id)
            if patient:
                st.session_state.current_patient = patient
                st.session_state.current_patient_id = patient_id
                st.success("Patient data loaded!")
        
        if hasattr(st.session_state, 'current_patient'):
            st.subheader("Update Patient Information")
            patient = st.session_state.current_patient
            
            with st.form("update_patient_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Full Name", value=patient.get('name', ''))
                    age = st.number_input("Age", min_value=1, max_value=120, value=patient.get('age', 30))
                    gender = st.selectbox("Gender", ["male", "female", "others"], 
                                        index=["male", "female", "others"].index(patient.get('gender', 'male')))
                
                with col2:
                    city = st.text_input("City", value=patient.get('city', ''))
                    height = st.number_input("Height (meters)", min_value=0.5, max_value=3.0, 
                                           value=patient.get('height', 1.75), step=0.01)
                    weight = st.number_input("Weight (kg)", min_value=10.0, max_value=500.0, 
                                           value=patient.get('weight', 70.0), step=0.1)
                
                submitted = st.form_submit_button("Update Patient")
                
                if submitted:
                    update_data = {
                        "name": name,
                        "city": city,
                        "age": age,
                        "gender": gender,
                        "height": height,
                        "weight": weight
                    }
                    
                    if update_patient(st.session_state.current_patient_id, update_data):
                        st.info("🔄 Patient updated! You can view the changes in 'View All Patients' or search by ID")
                        # Clear the form after successful update
                        del st.session_state.current_patient
                        del st.session_state.current_patient_id
                        st.rerun()
    
    elif page == "Delete Patient":
        st.header("🗑️ Delete Patient")
        st.warning("⚠️ This action cannot be undone!")
        
        patient_id = st.text_input("Enter Patient ID to delete:")
        
        if patient_id:
            # Store patient ID in session state when first entered
            st.session_state.delete_patient_id = patient_id
            
            # Show patient info before deletion
            patient = get_patient_by_id(patient_id)
            if patient:
                st.session_state.patient_to_delete = patient
                st.subheader("Patient to be deleted:")
                st.json(patient)
                
                # Use session state to track confirmation
                if 'delete_confirmed' not in st.session_state:
                    st.session_state.delete_confirmed = False
                
                if not st.session_state.delete_confirmed:
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        st.session_state.delete_confirmed = True
                        st.rerun()
                else:
                    # Actually delete the patient
                    if delete_patient(st.session_state.delete_patient_id):
                        st.success(f"✅ Patient {st.session_state.delete_patient_id} has been permanently deleted!")
                        # Clear all session state
                        st.session_state.delete_confirmed = False
                        if 'delete_patient_id' in st.session_state:
                            del st.session_state.delete_patient_id
                        if 'patient_to_delete' in st.session_state:
                            del st.session_state.patient_to_delete
                        st.info("🔄 You can verify the deletion in 'View All Patients'")
                    else:
                        # Reset on failure
                        st.session_state.delete_confirmed = False
        
        # If we have a patient in session state (after confirmation), show it
        elif hasattr(st.session_state, 'patient_to_delete') and st.session_state.delete_confirmed:
            st.subheader("Patient to be deleted:")
            st.json(st.session_state.patient_to_delete)
            
            # Show the actual delete action
            with st.spinner("Deleting patient..."):
                if delete_patient(st.session_state.delete_patient_id):
                    st.success(f"✅ Patient {st.session_state.delete_patient_id} has been permanently deleted!")
                    # Clear session state
                    st.session_state.delete_confirmed = False
                    del st.session_state.delete_patient_id
                    del st.session_state.patient_to_delete
                    st.info("🔄 You can verify the deletion in 'View All Patients'")
                else:
                    st.session_state.delete_confirmed = False
    
    elif page == "Sort Patients":
        st.header("📊 Sort Patients")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sort_by = st.selectbox("Sort by:", ["bmi", "weight", "height"])
        
        with col2:
            order = st.selectbox("Order:", ["asc", "desc"])
        
        if st.button("Sort Patients"):
            sorted_patients = sort_patients(sort_by, order)
            if sorted_patients:
                st.subheader(f"Patients sorted by {sort_by} ({order}ending)")
                
                # Add calculated BMI to display
                for patient in sorted_patients:
                    if "height" in patient and "weight" in patient:
                        patient["BMI"] = round(patient["weight"] / (patient["height"] ** 2), 2)
                
                st.dataframe(sorted_patients, use_container_width=True)
            else:
                st.warning("No patients found or unable to sort")


if __name__ == "__main__":
    main()
