# Нова реалізація — та сама обіцянка, інші нутрощі
class QueueNotifier(Notifier):
    def __init__(self, queue):
        self._queue = queue
    def notify(self, to, message):
        self._queue.publish("notifications", {"to": to, "message": message})

# Вибір реалізації за прапорцем — одне місце на весь застосунок
def make_notifier(flags):
    if flags.enabled("queue-notifications"):
        return QueueNotifier(message_queue)
    return LegacyMailerNotifier()
