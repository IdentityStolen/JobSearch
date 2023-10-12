FROM python:3.8.9-buster

WORKDIR /usajobs

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8888

CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "runserver"]
