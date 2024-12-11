# Use Python base image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy dependency-related files first to leverage caching
COPY requirements.txt /app/

# Install dependencies
RUN pip install -r requirements.txt

# Copy model and script (these change more often)
COPY svm_model.pkl /app/
COPY svm_inference.py /app/
COPY scaler.pkl /app/

# Expose port
EXPOSE 5001

# Run the inference script
CMD ["python", "svm_inference.py"]
