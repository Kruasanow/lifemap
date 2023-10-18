FROM python:latest

WORKDIR /app

COPY . /app

RUN apt update
RUN apt install postgresql -y
RUN chmod 777 install.sh
RUN ./install.sh 

RUN export DBPASSWORD='rusanow'
RUN export DBUSER='oleg'
RUN export DBNAME='flask_db'
RUN export DBAPPKEY='pizda'

EXPOSE 5555

CMD ['python3','main.py']
