# Burn Calories Simulator

A simple full-stack web app that estimates calories burned during activities and stores recent workout results in PostgreSQL.

## Tech stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python, FastAPI
- Database: PostgreSQL
- Containerization: Docker + Docker Compose

## Project structure

- frontend/public/: Nginx-served static assets
- backend/app/api/: HTTP route modules
- backend/app/services/: domain calculations
- backend/app/models.py: database models
- backend/app/schemas.py: API validation and response schemas
- docker-compose.yml: Local orchestration for frontend, backend, and database

The backend is organized by responsibility so API routes, business logic, and persistence can evolve independently. The containers use environment-based configuration, health checks, and production-style startup commands; deployment-specific secrets should be supplied through the environment rather than committed to the repository.

## Run locally

1. Start Docker services:
   ```bash
   docker compose up --build
   ```

2. Open the app in your browser:
   ```text
   http://localhost
   ```

3. API docs are available here:
   ```text
   http://localhost:8000/docs
   ```

4. To stop the app:
   ```bash
   docker compose down
   ```

## Check the PostgreSQL database

Once the app is running, you can inspect the database directly from the PostgreSQL Docker container:

```bash
docker compose exec db psql -U postgres -d burn_calories
```

Then run:

```sql
\dt
SELECT * FROM workout_entries ORDER BY created_at DESC;
SELECT * FROM users ORDER BY created_at DESC;
SELECT * FROM activities ORDER BY created_at DESC;
```

You can also check the number of saved records:

```sql
SELECT COUNT(*) FROM workout_entries;
```

PostgreSQL is intentionally not published to the host; connect through `docker compose exec` or expose it only in a local development override. Keep production credentials in environment or secret-manager configuration rather than committing them.

## API endpoints and curl examples

Base URL:

```bash
http://localhost:8000
```

### Health check

```bash
curl http://localhost:8000/health
```

Expected status: `200 OK`

Example response:

```json
{"status":"ok"}
```

### List activities

```bash
curl http://localhost:8000/api/activities
```

### Create an activity

The MET value must be greater than `0` and no more than `30`:

```bash
curl -X POST http://localhost:8000/api/activities \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rowing",
    "metValue": 7.0
  }'
```

The default activities are seeded automatically when the backend starts. Existing databases are upgraded with the user preference column automatically for this version; future schema changes should use a migration tool.

### Create a workout

```bash
curl -X POST http://localhost:8000/api/workouts \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "running",
    "durationMinutes": 30,
    "weightKg": 70
  }'
```

Expected status: `201 Created`

Example response:

```json
{
  "id": 1,
  "activity": "running",
  "durationMinutes": 30,
  "weightKg": 70.0,
  "caloriesBurned": 257.25
}
```

### List workouts

```bash
curl http://localhost:8000/api/workouts
```

Expected status: `200 OK`

Example response:

```json
[
  {
    "id": 1,
    "activity": "running",
    "durationMinutes": 30,
    "weightKg": 70.0,
    "caloriesBurned": 257.25,
    "createdAt": "2026-09-01T12:00:00+00:00"
  }
]
```

### Get one workout by id

```bash
curl http://localhost:8000/api/workouts/1
```

Expected status: `200 OK`

If the workout does not exist:

```bash
curl http://localhost:8000/api/workouts/999
```

Expected status: `404 Not Found`

Example response:

```json
{"detail":"Workout not found"}

### Update a workout

`PUT` replaces the workout values and recalculates the calories burned:

```bash
curl -X PUT http://localhost:8000/api/workouts/1 \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "cycling",
    "durationMinutes": 45,
    "weightKg": 70
  }'
```

Expected status: `200 OK`

If the workout does not exist, the API returns `404 Not Found`.

### Delete a workout

```bash
curl -i -X DELETE http://localhost:8000/api/workouts/1
```

Expected status: `204 No Content`

If the workout does not exist, the API returns `404 Not Found`.

### Create a user

Name, age, and email are required. Weight and height are optional:

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alex Smith",
    "age": 30,
    "email": "alex@example.com",
    "weightKg": 70,
    "heightCm": 175
  }'
```

Expected status: `201 Created`

### List users

```bash
curl http://localhost:8000/api/users
```

Expected status: `200 OK`

### Get one user by id

```bash
curl http://localhost:8000/api/users/1
```

Expected status: `200 OK`

If the user does not exist, the API returns `404 Not Found`.

Example missing-field response:

```json
{"detail":"Name, age, and email are required"}
```
```

### Invalid request example

```bash
curl -X POST http://localhost:8000/api/workouts \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "running",
    "weightKg": 70
  }'
```

Expected status: `400 Bad Request`

Example response:

```json
{"detail":"Missing required fields"}
```

### Common HTTP status codes

- `200 OK`: successful GET requests
- `201 Created`: successful POST request that creates a resource
- `204 No Content`: successful DELETE request
- `400 Bad Request`: missing or invalid request data
- `404 Not Found`: requested resource does not exist
- `500 Internal Server Error`: unexpected server-side failure

## Example activity

- Activity: Running
- Weight: 70 kg
- Duration: 30 minutes

The backend calculates calories burnt using the MET formula and saves the result in PostgreSQL.
