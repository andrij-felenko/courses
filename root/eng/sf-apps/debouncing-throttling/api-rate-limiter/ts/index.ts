export interface DebounceOptions {
  leading?: boolean;
  trailing?: boolean;
  maxWait?: number;
}

export interface ThrottleOptions {
  leading?: boolean;
  trailing?: boolean;
}

export interface DebouncedFunction<TArgs extends any[], TReturn> {
  (...args: TArgs): TReturn | undefined;
  cancel(): void;
  flush(): TReturn | undefined;
  isPending(): boolean;
}

export interface RafThrottledFunction<TArgs extends any[]> {
  (...args: TArgs): void;
  cancel(): void;
}
