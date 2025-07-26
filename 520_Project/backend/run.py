from app import create_app
from gevent.pywsgi import WSGIServer

app = create_app()

if __name__ == "__main__":
    http_server = WSGIServer(('', 8000), app)
    http_server.serve_forever()
