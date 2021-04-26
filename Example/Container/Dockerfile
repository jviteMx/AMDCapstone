FROM python:3.9.1

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /code/
EXPOSE 8080
CMD ["python", "app.py"]