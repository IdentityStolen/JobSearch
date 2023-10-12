# this didn't work due to directory issues for req.txt

FROM python:3.8

WORKDIR /usajobs

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8888

CMD ["python", "manage.py", "runserver"]