interface TransformStream<I = Uint8Array, O = Uint8Array> {
  readonly readable: ReadableStream<O>;
  readonly writable: WritableStream<I>;
}

interface Transformer<I, O> {
  start?(controller: TransformStreamDefaultController<O>): void;
  transform?(chunk: I, controller: TransformStreamDefaultController<O>): void | Promise<void>;
  flush?(controller: TransformStreamDefaultController<O>): void | Promise<void>;
}
