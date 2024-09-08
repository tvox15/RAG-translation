import requests
from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route("/api/hello")
def hello_world():
    return {
        "msg": "Hello, World!"
    }

# make a post route for translation
@app.route("/api/translate", methods=["POST"])
def translate():
    data = requests.get_json()
    text = data["text"]
    context = data["context"]

    print("Translating text: ", text)
    print("Context: ", context)


if __name__ == "__main__":
    # run on port 8080 and auto restart
    app.run(port=8080, debug=True)
    