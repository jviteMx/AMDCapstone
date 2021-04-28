FROM python:3.9.1

ENV PYTHONUNBUFFERED 1
RUN mkdir /dashboard
WORKDIR /dashboard
COPY ./dashboard /dashboard/
RUN pip install -r requirements.txt
EXPOSE 8082
CMD ["python", "app.py"]