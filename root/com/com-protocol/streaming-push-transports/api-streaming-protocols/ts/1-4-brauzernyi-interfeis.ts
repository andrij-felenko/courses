interface EventSourceInit {
  withCredentials?: boolean; // Дозволяє передачу авторизаційних кук та HTTP-заголовків при міждоменних CORS-запитах
}

class EventSource extends EventTarget {
  constructor(url: string | URL, eventSourceInitDict?: EventSourceInit);

  static readonly CONNECTING = 0; // Встановлення з'єднання або пауза перед повторною спробою
  static readonly OPEN = 1;       // З'єднання активне, потік подій приймається
  static readonly CLOSED = 2;     // З'єднання остаточно закрите викликом close() або фатальною помилкою

  readonly readyState: number;
  readonly url: string;
  readonly withCredentials: boolean;

  onopen: ((this: EventSource, ev: Event) => any) | null;
  onmessage: ((this: EventSource, ev: MessageEvent) => any) | null;
  onerror: ((this: EventSource, ev: Event) => any) | null;

  close(): void; // Примусово закриває TCP-з'єднання та блокує будь-які подальші спроби перепідключення
}
