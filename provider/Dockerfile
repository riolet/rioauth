#Currently, the dockerfile is mostly for use with hotbed.io CICD

FROM python:2.7.13-wheezy

RUN ls && cp config.default config \
&& sed -i 's/https/http/i' config \
&& sed -i 's/www.example.com/provider-rioauth.hotbed.io/i' config \
&& sed -i 's/smtp.gmail.com/smtp.example.com/i' config

RUN pip install -r requirements.txt

RUN python test_db_data.py

RUN chown -R :0 data && chmod -R 775 data && chmod g+s data

CMD python server.py