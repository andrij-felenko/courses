// ХИБНО: порт дзеркалить постачальника — його модель протекла у ваше ядро.
interface Mailer {
  sendViaSendGrid(msg: SendGridMessage): Promise<SendGridResponse>;
}

// ПРАВИЛЬНО: порт у ВАШИХ термінах — постачальника не видно зовсім.
interface Notifier {
  notify(to: Recipient, event: DomainEvent): Promise<void>;
}
// Конкретний SendGrid (чи SMTP, чи будь-що) живе В АДАПТЕРІ,
// що реалізує Notifier, і ніде більше про нього не знають.
