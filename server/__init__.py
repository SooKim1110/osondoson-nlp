from flask import Flask

app = Flask(__name__)

# if __name__=='__main__':
#  app.run(host='0.0.0.0', port=5000, debug=True)

import server.api.sentiment
import server.api.summary
import server.api.voice
import server.api.emergency
