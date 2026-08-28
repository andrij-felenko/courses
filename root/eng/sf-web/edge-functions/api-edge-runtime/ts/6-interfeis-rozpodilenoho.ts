interface KVNamespace {
  get(key: string, options?: { cacheTtl?: number }): Promise<string | null>;
  get<T>(key: string, options: { type: 'json'; cacheTtl?: number }): Promise<T | null>;
  get(key: string, options: { type: 'arrayBuffer'; cacheTtl?: number }): Promise<ArrayBuffer | null>;
  get(key: string, options: { type: 'stream'; cacheTtl?: number }): Promise<ReadableStream | null>;

  getWithMetadata<T = unknown, M = unknown>(
    key: string,
    options?: { type: 'json'; cacheTtl?: number }
  ): Promise<{ value: T | null; metadata: M | null }>;

  put(
    key: string,
    value: string | ArrayBuffer | ReadableStream,
    options?: { expiration?: number; expirationTtl?: number; metadata?: unknown }
  ): Promise<void>;

  delete(key: string): Promise<void>;

  list<M = unknown>(options?: {
    prefix?: string;
    limit?: number;
    cursor?: string;
  }): Promise<{
    keys: Array<{ name: string; expiration?: number; metadata?: M }>;
    list_complete: boolean;
    cursor?: string;
  }>;
}
