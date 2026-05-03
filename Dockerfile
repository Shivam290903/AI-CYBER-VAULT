# Use an official Python runtime as a parent image
 # Use an official Python runtime as a parent image
FROM python:3.11-slim
# Set the working directory
WORKDIR /app

# Install system dependencies, including Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port Render uses
EXPOSE 10000

# Run the application using Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]