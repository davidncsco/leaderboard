FROM python:3.8.9-slim

COPY ./leader.py /app/
COPY ./requirements.txt /app
COPY ./templates /app/templates

WORKDIR /app

RUN pip3 install -r requirements.txt

ENV DATABASE_URL='sqlite://db.sqlite3'

EXPOSE 8000

CMD ["uvicorn", "leader:app", "--host=0.0.0.0", "--reload"]