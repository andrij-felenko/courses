# Концерн вписаний у справу: логування переплетене з роботою
class OrderService:
    def place_order(self, order):
        log.info("place_order: in")          # концерн
        try:
            result = self._do_place(order)   # справа
            log.info("place_order: ok")      # концерн
            return result
        except Exception:
            log.exception("place_order: err")  # концерн
            raise
