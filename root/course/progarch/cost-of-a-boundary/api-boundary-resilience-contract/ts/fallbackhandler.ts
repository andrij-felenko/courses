export enum BoundaryStatus {
  SUCCESS = 'SUCCESS',
  TIMEOUT = 'TIMEOUT',
  CIRCUIT_OPEN = 'CIRCUIT_OPEN',
  RETRIES_EXCEEDED = 'RETRIES_EXCEEDED',
  FALLBACK_APPLIED = 'FALLBACK_APPLIED',
}

export interface ResilientResult<T> {
  readonly value: T;
  readonly isFallback: boolean;
  readonly status: BoundaryStatus;
  readonly attempts: number;
  readonly executionTimeMs: number;
  readonly originalError?: Error;
}

export type FallbackHandler<T> = (
  error: Error,
  context: { readonly attemptCount: number; readonly status: BoundaryStatus }
) => Promise<T> | T;
