import threading


_lock = threading.Lock()
_blockers = set()


def block_wake(source):
    with _lock:
        _blockers.add(str(source))


def unblock_wake(source):
    with _lock:
        _blockers.discard(str(source))


def wake_is_blocked():
    with _lock:
        return len(_blockers) > 0


def get_blockers():
    with _lock:
        return list(_blockers)