#!/usr/bin/python3
# Run a test server.
from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, env="development")
