#Currently, the dockerfile is mostly for use with hotbed.io CICD

FROM python:2.7.13-wheezy

RUN cp config.default config && sed -i 's/https/http/i' config && sed -i
's/www.example.com/provider-rioauth.hotbed.io/i' config && sed -i
's/smtp.gmail.com/smtp.example.com/i' config

RUN pip install -r requirements.txt

RUN openssl req -x509 -sha256 -nodes -newkey rsa:2048 -days 365 -keyout
localhost.key -out localhost.crt  -subj
"/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.example.com"

RUN python test_db_data.py

RUN chown -R :0 data && chmod -R 775 data && chmod g+s data

CMD python server.py