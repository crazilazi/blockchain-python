from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def helloworld():
    return 'Heya, im here'


app.run('0.0.0.0', 4000)
