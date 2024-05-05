FROM python:3.11-alpine

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY /src /app

ENTRYPOINT [ "uvicorn", "main:app", "--proxy-headers", "--host" ,"0.0.0.0", "--port", "3000"]