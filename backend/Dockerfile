FROM python:3.10-slim

ENV PYTHONBYTECODE=1
ENV PYTHONBUFFERCODE=1

WORKDIR /app
COPY requirements.txt . 


# RUN pip install --upgrade pip setuptools

RUN pip install --no-cache-dir -r requirements.txt


COPY ./app /app

EXPOSE 8000

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" ]