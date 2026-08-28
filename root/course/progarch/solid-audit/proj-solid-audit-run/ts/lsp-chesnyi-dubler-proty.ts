// чесний: сток видимий, контракт справді виконано
export class RecordingNotifier implements Notifier {
  readonly sent: Message[] = [];
  async send(m: Message): Promise<void> { this.sent.push(m); }
}

// ПАСТКА: форма правильна, поведінка бреше — «send» нічого не робить
export class SilentNotifier implements Notifier {
  async send(_m: Message): Promise<void> { /* вдає, що надіслав */ }
}
