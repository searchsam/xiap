#!/usr/bin/python3
# Run a test server.
from app import app
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(".") / ".flaskenv"
load_dotenv(dotenv_path=env_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    # app.run(env="development", host="0.0.0.0", port=5000, debug=True)
