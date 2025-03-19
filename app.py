from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Railway!'

port = int(os.environ.get('PORT', 5001))
app.run(host='0.0.0.0', port=port)
