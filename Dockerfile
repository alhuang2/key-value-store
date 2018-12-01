FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

ENTRYPOINT ["python3"]
CMD ["manage.py","runserver","0.0.0.0:8080"]