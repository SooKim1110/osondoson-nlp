from flask import Flask
from flask import Response

app = Flask(__name__)

@app.route('/', methods=['GET'])
def default_route():
    return Response(status=200)

import analyze_server.api.sentiment
import analyze_server.api.summary
# import server.api.voice
