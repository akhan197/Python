import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Server is running!"

import os

port = int(os.environ.get("PORT", 8080))  # Default to 8080 if not set
print(f"Starting Flask on port {port}")

app.run(host="0.0.0.0", port=port)
