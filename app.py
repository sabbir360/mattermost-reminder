from flask import Flask, request, jsonify
# from requests import request as curl_request
from config import *

app = Flask(__name__)


@app.route('/', methods=['POST'])
def reminder():
    data = request.form
    reply = {}
    if data.get("token", None):
        print(request.form)
    else:
        reply["text"] = "Invalid Slash Token"
    return jsonify(reply)


if __name__ == "__main__":
    app.run(debug=DEBUG, host=HOST, port=PORT)
