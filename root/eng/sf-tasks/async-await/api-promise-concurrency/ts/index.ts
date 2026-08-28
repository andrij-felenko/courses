interface AbortSignal {
  readonly aborted: boolean;
  readonly reason: unknown;
  addEventListener(type: "abort", listener: (ev: Event) => void): void;
  removeEventListener(type: "abort", listener: (ev: Event) => void): void;
  throwIfAborted(): void;
}

interface AbortController {
  readonly signal: AbortSignal;
  abort(reason?: unknown): void;
}
