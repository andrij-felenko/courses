class WebSocket extends EventTarget {
  constructor(url: string | URL, protocols?: string | string[]);

  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSING = 2;
  static readonly CLOSED = 3;

  readonly readyState: number;
  readonly url: string;
  readonly protocol: string;       // Узгоджений підпротокол із Sec-WebSocket-Protocol
  readonly extensions: string;     // Узгоджені розширення (наприклад, permessage-deflate)
  readonly bufferedAmount: number; // Кількість байтів у вихідній черзі браузера (індикатор backpressure)

  binaryType: BinaryType; // "blob" або "arraybuffer"

  onopen: ((this: WebSocket, ev: Event) => any) | null;
  onmessage: ((this: WebSocket, ev: MessageEvent) => any) | null;
  onerror: ((this: WebSocket, ev: Event) => any) | null;
  onclose: ((this: WebSocket, ev: CloseEvent) => any) | null;

  send(data: string | ArrayBufferLike | Blob | ArrayBufferView): void;
  close(code?: number, reason?: string): void;
}
