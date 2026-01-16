# Academic Program Reporting Dashboard

A dashboard for tracking university collaborations with Tenstorrent, pulling data from Asana and displaying metrics with historical growth trends.

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Frontend:** React, TypeScript, Recharts, React Query
- **Integration:** Asana API

## Prerequisites

- Python 3.9+
- Node.js 18+
- Asana Personal Access Token

## Setup

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 2. Configure Asana Credentials

Edit `backend/.env` with your Asana credentials:

```env
ASANA_ACCESS_TOKEN=your_personal_access_token
ASANA_PROJECT_GID=your_project_id
ASANA_FIELD_RESEARCHERS_COUNT=field_gid
ASANA_FIELD_STUDENTS_COUNT=field_gid
ASANA_FIELD_HARDWARE_TYPES=field_gid
```

**How to get these values:**

1. **Personal Access Token:** Go to [Asana Developer Console](https://app.asana.com/0/developer-console) → Create new token

2. **Project GID:** Open your Asana project in browser. The URL will be `https://app.asana.com/0/PROJECT_GID/...`

3. **Custom Field GIDs:** Run this command after setting your token and project GID:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://app.asana.com/api/1.0/projects/YOUR_PROJECT_GID?opt_fields=custom_field_settings.custom_field.name,custom_field_settings.custom_field.gid"
   ```

**Note:** The university name is pulled from the Asana task name itself, not from a custom field.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Start the Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Start the Frontend

```bash
cd frontend
npm run dev
```

The dashboard will be available at `http://localhost:5173`

## Usage

1. Open the dashboard at `http://localhost:5173`
2. Click "Sync from Asana" to pull data from your Asana project
3. View metrics:
   - **Metric Cards:** Total universities, researchers, and students with 30-day growth
   - **Growth Chart:** Historical trends over time (toggle metrics on/off)
   - **University Table:** Searchable and sortable list of all universities

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/metrics/current` | Current aggregate metrics |
| GET | `/api/v1/metrics/timeline` | Historical data for charts |
| GET | `/api/v1/metrics/growth` | Growth percentages |
| GET | `/api/v1/universities/` | List all universities |
| POST | `/api/v1/sync/trigger` | Trigger Asana sync |
| GET | `/api/v1/sync/status` | Sync status |

## Database

The application uses SQLite for storing historical snapshots. The database file (`academic_program.db`) is created automatically in the `backend/` directory on first run.

To reset the database, delete the file and restart the backend.
