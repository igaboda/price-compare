FROM python:3.9
ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY ./app .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
VOLUME /app/db
EXPOSE 8000
