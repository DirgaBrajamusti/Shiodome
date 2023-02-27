FROM python:3.10-slim

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--bind=0.0.0.0:5000", "--log-level=debug", "app:app"]