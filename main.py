"""Patient Management API

This small FastAPI application serves a JSON-backed list of patients. The
project is intentionally lightweight: data are read from `patients.json` on
each request so the app remains simple to run and inspect during
development.
"""

from typing import Any, Dict, List, Annotated, Literal, Optional
from pydantic import BaseModel, Field, computed_field
from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
# load/save helpers live in `util.py` to keep `main.py` focused on routes.
from util import load_data, save_data

app = FastAPI(title="Patient Management System", version="1.0")

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="The unique identifier for the patient", example="P001")]
    name: Annotated[str, Field(..., min_length=2, max_length=50, description="Full name of the patient", example="John Doe")]
    city: Annotated[str, Field(..., min_length=2, max_length=100, description="City where the patient resides", example="New York")]
    age: Annotated[int, Field(..., gt=0, description="Age must be a positive integer")]
    gender: Annotated[Literal["male", "female", "others"], Field(..., description="Gender of the patient", example="male")]
    height: Annotated[float, Field(..., gt=0, description="Height must be a positive number and in meters")]
    weight: Annotated[float, Field(..., gt=0, description="Weight must be a positive number and in kilograms")]

    @computed_field
    @property
    def bmi(self) -> float:
        """Calculate and return the Body Mass Index (BMI) for the patient."""
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        """Provide a health verdict based on the BMI value."""
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "Normal weight"
        elif 25 <= self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obesity"
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal["male", "female", "others"]], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


@app.get("/", summary="Health / basic info")
def hello_world() -> Dict[str, str]:
    """A tiny health-check and entry point.

    Returns a short message so you can verify the app is running in a
    browser or curl without loading other endpoints.
    """
    return {"message": "Patient Management System"}


@app.get("/about", summary="About this service")
def about() -> Dict[str, str]:
    """Short description useful for documentation pages or service checks."""
    return {"message": "A simple, file-backed Patient Management System"}


@app.get("/view", summary="Return all patients")
def view_patients() -> Dict[str, Any]:
    """Return the raw patients dictionary.

    This endpoint returns the file contents exactly as stored. Consumers can
    decide how to present or paginate the results.
    """
    return load_data()


@app.get("/patient/{patient_id}", summary="Get patient by ID")
def view_patient(
    patient_id: str = Path(..., description="The ID of the patient to retrieve", example="P001")
) -> Dict[str, Any]:
    """Return a single patient record.

    The function normalizes the provided id (strip + upper) so callers don't
    need to worry about whitespace or case. If the patient is not found the
    endpoint returns a 404.
    """
    data = load_data()
    patient_id = patient_id.strip().upper()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")


@app.get("/sort/", summary="Sort patients by a numeric field")
def sort_patients(
    sort_by: str = Query(..., description="The field to sort by", example="bmi"),
    order: str = Query("asc", description="Sort order: asc or desc", example="asc"),
) -> List[Dict[str, Any]]:
    """Return patients sorted by a numeric field.

    The function checks the inputs and returns clear HTTP errors for invalid requests. Results are alist of patient records (not the keyed dict) which is convenient for
    frontends that render tables.
    """
    valid_sort_fields = ["bmi", "weight", "height"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Must be one of {valid_sort_fields}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order. Must be 'asc' or 'desc'")
    data = load_data()
    # sort the dict values by the requested numeric key
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=(order == "desc"))
    return sorted_data


@app.post("/create/", summary="Add a new patient")
def create_patient(patient: Patient) -> Dict[str, Any]:
    """Add a new patient record."""
    data = load_data()
    # Check if tyhe patient ID already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient ID already exists")
    # Add the new patient to the data
    data[patient.id] = patient.model_dump(exclude=['id'])
    # Save the updated data back to the JSON file
    save_data(data)
    return JSONResponse(status_code=201, content={"message": "Patient created successfully", "patient": patient.model_dump() })

@app.put("/edit/{patient_id}", summary="Update an existing patient")
def update_patient(patient_id:str,patient_update: PatientUpdate):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    existing_patient = data[patient_id]
    patient_update_dict = patient_update.model_dump(exclude_unset=True)
    for key, value in patient_update_dict.items():
        existing_patient[key] = value

    existing_patient['id'] = patient_id
    patient_pydentic_obj = Patient(**existing_patient)

    existing_patient = patient_pydentic_obj.model_dump(exclude=['id'])
    data[patient_id] = existing_patient
    # Update the patient record in the data
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient updated successfully", "patient": existing_patient })


@app.delete("/delete/{patient_id}", summary="Delete a patient by ID")
def delete_patient(
    patient_id: str = Path(..., description="The ID of the patient to delete", example="P001")
) -> Dict[str, str]:
    """Delete a patient record by ID.

    If the patient is not found the endpoint returns a 404.
    """
    data = load_data()
    patient_id = patient_id.strip().upper()
    if patient_id in data:
        del data[patient_id]
        save_data(data)
        return {"message": "Patient deleted successfully"}
    raise HTTPException(status_code=404, detail="Patient not found")