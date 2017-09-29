from flask import *
from flask_eventsource import *
import time
from gevent.wsgi import WSGIServer

app = Flask(__name__)
sse = SSEHandler(app)

@app.route("/")
def index():
	return """<html>
<head>
<title>SSETest</title>
</head>
<body>
<div id="test">
<h1>EventSource testing</h1>
<p>Go to the URL below to update this, as well as all other working screens.</p>
</div>
<a href="/update" target="_blank">Update</a>
<script>
window.onload=function() {
	var source = new EventSource("/subscribe");
	source.onmessage = function(e) {
		document.getElementById("test").innerHTML = e.data;
	};
};
</script>
</body>
</html>"""

@app.route("/subscribe")
def subscribe():
	return sse.eventsource()

@app.route("/update")
def update():
	sse.publish("<h1>EventSource testing!</h1><p>The time is: {!s}</p>".format(time.time()))
	return "Updated"

if __name__=="__main__":
	app.debug=True
	server = WSGIServer(("0.0.0.0",1045),app)
	server.serve_forever()
