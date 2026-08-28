// Нова реалізація — та сама обіцянка, інші нутрощі
class QueueNotifier implements Notifier {
  constructor(private queue: MessageQueue) {}
  notify(to: string, message: string) {
    this.queue.publish("notifications", { to, message });
  }
}

// Вибір реалізації за прапорцем — одне місце на весь застосунок
function makeNotifier(flags: Flags): Notifier {
  return flags.enabled("queue-notifications")
    ? new QueueNotifier(messageQueue)
    : new LegacyMailerNotifier();
}
