import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask app is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 0))  # Default to dynamic port
    app.run(host="0.0.0.0", port=port)
