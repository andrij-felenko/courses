interface ResponseInit {
  status?: number;
  statusText?: string;
  headers?: HeadersInit;
}

interface Response {
  readonly status: number;
  readonly statusText: string;
  readonly ok: boolean;
  readonly headers: Headers;
  readonly body: ReadableStream<Uint8Array> | null;
  readonly bodyUsed: boolean;

  clone(): Response;
  arrayBuffer(): Promise<ArrayBuffer>;
  json<T = unknown>(): Promise<T>;
  text(): Promise<string>;
}
