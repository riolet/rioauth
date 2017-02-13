FROM python:2.7.13-wheezy

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

RUN python test_db_data.py

RUN chown -R :0 /tmp/rioauth/ && chmod -R 775 /tmp/rioauth/ && chmod g+s /tmp/rioauth/

CMD python server.py