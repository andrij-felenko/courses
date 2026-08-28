interface Request {
  readonly method: string;
  readonly url: string;
  readonly headers: Headers;
  readonly body: ReadableStream<Uint8Array> | null;
  readonly bodyUsed: boolean;
  readonly redirect: RequestRedirect;
  readonly signal: AbortSignal;
  readonly cf?: IncomingRequestCfProperties;

  clone(): Request;
  arrayBuffer(): Promise<ArrayBuffer>;
  blob(): Promise<Blob>;
  json<T = unknown>(): Promise<T>;
  text(): Promise<string>;
}
