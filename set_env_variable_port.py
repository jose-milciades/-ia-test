from dotenv import load_dotenv
import os
import random

load_dotenv()

if __name__ == "__main__":
    try:
        if int(os.environ.get("FLASK_PORT_RANDOM")) == 1:
            port = str(random.randint(
                    int(os.environ.get("START_RANDOM_PORT")),
                    int(os.environ.get("END_RANDOM_PORT"))
                )
            )
        else:
            if os.environ.get("CLIENT") == "1":
                port = os.environ.get("CLIENT_PORT")
            else:
                port = os.environ.get("TEST_PORT")
    except Exception as e: 
        print(f"Error: {e}")
        port = "4503"
    os.environ["FLASK_PORT"] = port

    file_ = ""
    with open(".env", "r+") as f:
        lines = f.readlines()
        added = False
        for line in lines:
            if line.find("FLASK_PORT") != -1 and line.find("FLASK_PORT_TEST") == -1:
                line = "FLASK_PORT = "+port+"\n"
                added = True
            file_ = file_+line
        if not added:
            line = "\nFLASK_PORT = "+port+"\n"
            file_ = file_+line
        f.seek(0)
        f.write(file_)
        f.truncate()

    with open("port_env_variable.txt", "w+") as f:
        f.write(f"export FLASK_PORT={port}")

    print(f"PORT: {os.environ['FLASK_PORT']}")