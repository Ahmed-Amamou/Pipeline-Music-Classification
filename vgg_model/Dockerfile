FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
# Set environment variable to disable GPU
ENV CUDA_VISIBLE_DEVICES=""
EXPOSE 5000
CMD ["python", "app.py"]
