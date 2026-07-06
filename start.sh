#!/bin/bash

# Start the backend
cd backend
source venv/bin/activate
uvicorn app.main:app --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Start the frontend
cd frontend
npm run dev -- -p 3000 &
FRONTEND_PID=$!
cd ..

echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:3000"

# Wait for both processes
wait $BACKEND_PID
wait $FRONTEND_PID
