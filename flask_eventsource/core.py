import gevent
from gevent.queue import Queue
from flask import Response

class SSE:
	def __init__(self,data,event="",id=""):
		self.event = dict(event=event,id=id,data=data)

	def encode(self):
		return "\n".join(["{}: {}".format(k, self.event[k] if self.event[k] else " ".strip()) for k in self.event.keys()])+"\n\n"

class SubscriptionHandler:
	"""Handles subscriptions."""
	def __init__(self):
		self.subs = []

	def subscribe(self):
		q = Queue()
		self.subs.append(q)
		return q

	def unsubscribe(self,q):
		self.subs.remove(q)

	def notify(self,data,event=None,id=None):
		ev = SSE(data,event,id)
		def send():
			for q in self.subs[:]:
				q.put(ev.encode())
		gevent.spawn(send)

class SSEHandler:
	def __init__(self,app=None,blueprint=None):
		self.app=app
		self.blueprint=blueprint
		self.subhandler = SubscriptionHandler()
		if app is not None:
			self.init_app()
		elif blueprint is not None:
			self.init_bp()

	def init_app(self):
		self.app.ssehandler = self
	
	def init_bp(self):
		self.blueprint.ssehandler = self

	"""Returns a request object that handles SSE"""
	def eventsource(self):
		def gen():
			q = self.subhandler.subscribe()
			try:
				while True:
					result = q.get()
					yield result # event is pre-encoded in queue!
			except GeneratorExit:
				self.subhandler.unsubscribe(q)
		return Response(gen(), mimetype="text/event-stream")

	def publish(self,*args,**kw):
		self.subhandler.notify(*args,**kw)
