from flask import Flask
from flask import Response

app = Flask(__name__)

@app.route('/', methods=['GET'])
def default_route():
    return Response(status=200)

import server.api.sentiment
import server.api.summary
# import server.api.voice
