FROM python:3.9.7-slim

RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN pip3 install -r requirements.txt

RUN apt-get update && apt-get install -y openssh-client

EXPOSE 5000
CMD ["python", "/app/app.py"]