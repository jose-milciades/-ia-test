from app import app
from dotenv import load_dotenv
import os
import py_eureka_client.eureka_client as eureka_client
import random
import logging
import gc
from urllib.error import URLError

logging.getLogger().setLevel(logging.INFO)
load_dotenv()

logging.info("STARTING FLASK IA-TEST")

host = os.environ.get("HOST_FLASK")
if host is None:
    host = os.environ.get("HOST_FLASK_TEST")
logging.info(f"Host flask: {host}")

try:
    port = os.environ.get("FLASK_PORT")
    if port is None:
        port = os.environ.get("FLASK_PORT_TEST")
    port = int(port)
except: 
    port = 4503
logging.info(f"Starting in port: {port}")

eureka_server = os.environ.get("EUREKA_SERVER")
logging.info(f"Eureka server: {eureka_server}")

eureka_service_name = os.environ.get("EUREKA_APP_NAME")
logging.info(f"Eureka server name: {eureka_service_name}")

debug = True
should_register=True

if os.environ.get("LAUNCH_EUREKA") == "1":
    logging.info(f"Launching eureka...")
    try: 
        eureka_client.init(eureka_server=eureka_server,
                    app_name=eureka_service_name,
                    instance_port=port,
                    instance_host=host
                    )
    except URLError as e:
        pass
    debug = False

gc.collect()
#instance_host="192.168.100.4"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=debug)
