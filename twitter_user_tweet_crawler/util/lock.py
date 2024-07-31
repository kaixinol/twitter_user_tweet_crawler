import threading

lock: dict[int, bool] = {}
mutex = threading.Lock()


def update(data: dict):
    global lock
    lock |= data


def get():
    global lock
    return lock
