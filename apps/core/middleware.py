import threading

# Objet Thread-Local pour stocker la requête
_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, "request", None)


class ThreadLocalMiddleware:
    """Middleware pour stocker la requête courante dans un thread-local."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response
