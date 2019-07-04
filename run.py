#!/usr/bin/python3
# Run a test server.
import os
from app import app

os.putenv("FLASK_APP", "run.py")
os.putenv("AUTHLIB_INSECURE_TRANSPORT", "1")
os.putenv("FLAK_ENV", "development")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
