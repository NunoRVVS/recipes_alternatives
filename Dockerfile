# 1. Use an official Python base image
# 'slim' versions are smaller and more secure for cloud-native apps
FROM python:3.11-slim

# 2. Set the working directory inside the container
# All subsequent commands will run in this folder
WORKDIR /app

# 3. Copy only the requirements file first
# This is a Docker "Best Practice"—it caches your dependencies 
# so rebuilding code is much faster.
COPY requirements.txt .

# 4. Install the Python libraries
RUN pip install google-genai fastapi uvicorn pydantic python-dotenv

# 5. Copy the rest of your application code 
# (This includes main.py and your .env file if needed)
COPY . .

# 6. Inform Docker that the container listens on port 8000
EXPOSE 8000

# 7. The command to start your FastAPI server
# 0.0.0.0 allows the container to accept external traffic (Cloud/Localhost)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]