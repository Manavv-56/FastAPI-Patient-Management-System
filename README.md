## Patient Management System (FastAPI)

This is a complete Patient Management API built with FastAPI that serves
patient data from a local JSON file (`patients.json`). The project includes
both a REST API backend and a Streamlit web interface for easy interaction.

## Quick Start

1. **Clone the repository and navigate to the project directory**

2. **Create and activate a virtual environment:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Run the FastAPI server:**

```bash
uvicorn main:app --reload --port 8002
```

5. **Run the Streamlit demo (optional, in a new terminal):**

```bash
streamlit run streamlit_demo.py
```

## API Endpoints

### Health & Info
- `GET /` - Health check and basic info
- `GET /about` - Service description

### Patient Operations
- `GET /view` - Get all patients (returns dictionary keyed by patient ID)
- `GET /patient/{patient_id}` - Get patient by ID (case-insensitive)
- `POST /create/` - Create a new patient
- `PUT /edit/{patient_id}` - Update an existing patient
- `DELETE /delete/{patient_id}` - Delete a patient by ID

### Data Operations
- `GET /sort/?sort_by={field}&order={asc|desc}` - Sort patients by field (bmi, weight, height)

## API Examples

### Get all patients
```bash
curl http://127.0.0.1:8002/view
```

### Get a specific patient
```bash
curl http://127.0.0.1:8002/patient/P001
```

### Create a new patient
```bash
curl -X POST http://127.0.0.1:8002/create/ \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "P031",
    "name": "John Doe",
    "city": "New York",
    "age": 30,
    "gender": "male",
    "height": 1.75,
    "weight": 70
  }'
```

### Update a patient
```bash
curl -X PUT http://127.0.0.1:8002/edit/P001 \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Jane Doe",
    "age": 25
  }'
```

### Delete a patient
```bash
curl -X DELETE http://127.0.0.1:8002/delete/P001
```

### Sort patients by BMI
```bash
curl "http://127.0.0.1:8002/sort/?sort_by=bmi&order=desc"
```

## Interactive Documentation

- **Swagger UI:** http://127.0.0.1:8002/docs
- **ReDoc:** http://127.0.0.1:8002/redoc

## Streamlit Web Interface

The project includes a complete web interface built with Streamlit that provides:

- View all patients in a table
- Search for specific patients
- Create new patients with form validation
- Update existing patient information
- Delete patients with confirmation
- Sort patients by various fields

Access the web interface at: http://localhost:8501 (after running `streamlit run streamlit_demo.py`)

## Project Structure

```
├── main.py              # FastAPI application with all endpoints
├── util.py              # Data persistence helpers (load/save JSON)
├── streamlit_demo.py    # Streamlit web interface
├── patients.json        # Patient data storage
├── requirements.txt     # Python dependencies
├── run_demo.sh         # Script to run both servers
└── README.md           # This file
```

## Patient Data Model

Each patient record contains:

- `id` (string): Unique patient identifier (e.g., "P001")
- `name` (string): Full name (2-50 characters)
- `city` (string): City of residence (2-100 characters)
- `age` (integer): Age in years (> 0)
- `gender` (string): "male", "female", or "others"
- `height` (float): Height in meters (> 0)
- `weight` (float): Weight in kilograms (> 0)

The API automatically calculates BMI and health verdict based on height and weight.

## Demo


# FASTAPI Docs
<img width="1420" height="739" alt="Screenshot 2025-09-16 at 23 22 53" src="https://github.com/user-attachments/assets/eee94a80-15b2-4768-ae73-bfc8a940ac6e" />


