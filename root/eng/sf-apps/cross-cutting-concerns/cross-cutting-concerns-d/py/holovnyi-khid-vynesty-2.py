# Концерн — обгортка. Справа не знає, що її логують.
def logged(fn):
    def wrapper(*args, **kwargs):
        log.info(f"{fn.__name__}: in")
        try:
            r = fn(*args, **kwargs)
            log.info(f"{fn.__name__}: ok")
            return r
        except Exception:
            log.exception(f"{fn.__name__}: err")
            raise
    return wrapper

class OrderService:
    @logged
    def place_order(self, order):
        return self._do_place(order)   # лише справа, нічого зайвого
