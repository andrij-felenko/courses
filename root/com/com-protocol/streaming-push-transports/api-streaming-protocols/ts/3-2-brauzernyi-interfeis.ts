class WebTransport {
  constructor(url: string | URL, options?: WebTransportOptions);

  readonly ready: Promise<void>;   // Виконується після завершення QUIC-рукостискання
  readonly closed: Promise<WebTransportCloseInfo>; // Виконується при закритті сесії

  // Ненадійні датаграми (аналог UDP без гарантії доставки)
  readonly datagrams: WebTransportDatagramDuplexStream;

  // Надійні незалежні потоки (аналог паралельних TCP-каналів)
  createBidirectionalStream(): Promise<WebTransportBidirectionalStream>;
  createUnidirectionalStream(): Promise<WritableStream<Uint8Array>>;

  readonly incomingBidirectionalStreams: ReadableStream<WebTransportBidirectionalStream>;
  readonly incomingUnidirectionalStreams: ReadableStream<ReadableStream<Uint8Array>>;

  close(closeInfo?: WebTransportCloseInfo): void;
}
