FROM python:3.7-slim

WORKDIR /app

ADD requeriments.txt requeriments.txt

RUN pip install --no-cache-dir -r requirements.txt

ADD set_env_variable_port.py /app
ADD run.py /app
ADD entrypoint.sh /app
ADD .env /app

ADD app/. /app/app/

ENV CLIENT=0
ENV FLASK_PORT_RANDOM=0
ENV START_RANDOM_PORT=4503
ENV END_RANDOM_PORT=4503
ENV CLIENT_PORT=4502
ENV TEST_PORT=4503
ENV LAUNCH_EUREKA=0
ENV EUREKA_SERVER_CLIENT="http://192.168.0.22:8762/eureka"
ENV EUREKA_SERVER_TEST="http://192.168.0.22:8763/eureka"
ENV EUREKA_APP_NAME="servicio-ia-test"
ENV HOST_FLASK="192.168.0.11"

COPY entrypoint.sh /entrypoint.sh

RUN chmod 777 /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
#CMD [ "python3", "run.py" ]