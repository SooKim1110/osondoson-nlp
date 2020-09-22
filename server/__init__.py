from flask import Flask

app = Flask(__name__)

# if __name__=='__main__':
#  app.run(host='0.0.0.0', port=5000, debug=True)

import server.sentiment
import server.summary
import server.voice
import server.emergency
