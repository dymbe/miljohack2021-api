FROM python:3.8-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000
RUN python dbutils.py
CMD python app.py
