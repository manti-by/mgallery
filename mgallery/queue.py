from redis import Redis
from rq import Queue

queue = Queue("mgallery", connection=Redis())
