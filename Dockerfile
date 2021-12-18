FROM python:3.8.9-slim

COPY ./leader.py /app/
COPY ./requirements.txt /app
COPY ./static /app/static
COPY ./templates /app/templates

WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "leader:app", "--host=0.0.0.0", "--reload"]