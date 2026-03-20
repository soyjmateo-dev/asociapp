import threading

_thread_locals = threading.local()


def set_current_tenant(db_name):
    _thread_locals.db_name = db_name


def get_current_tenant():
    return getattr(_thread_locals, "db_name", None)
