import os

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello Akhshy!! Its working"

@app.route("/test")
def hello_world():
    return "Hello Akhshy!! Its working even after updating in github"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))