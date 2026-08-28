// TypeScript: Ідіоматична реалізація DataLoader з чергою мікротасок

type BatchFunction<K, V> = (keys: ReadonlyArray<K>) => Promise<Array<V | Error>>;

interface DataLoaderOptions<K> {
  maxBatchSize?: number;
  cache?: boolean;
  cacheKeyFn?: (key: K) => string;
}

export class DataLoader<K, V> {
  private readonly batchFn: BatchFunction<K, V>;
  private readonly maxBatchSize: number;
  private readonly useCache: boolean;
  private readonly cacheKeyFn: (key: K) => any;
  
  // Черга ключів та відповідних їм Promise triggers для поточного пакета
  private queue: Array<{
    key: K;
    resolve: (value: V) => void;
    reject: (error: Error) => void;
  }> = [];
  
  // Локальний мемоізаційний кеш у межах одного екземпляра
  private cacheMap: Map<any, Promise<V>> = new Map();
  private batchScheduled: boolean = false;

  constructor(batchFn: BatchFunction<K, V>, options: DataLoaderOptions<K> = {}) {
    this.batchFn = batchFn;
    this.maxBatchSize = options.maxBatchSize ?? 1000;
    this.useCache = options.cache ?? true;
    this.cacheKeyFn = options.cacheKeyFn ?? ((k: K) => k);
  }

  public load(key: K): Promise<V> {
    const cacheKey = this.cacheKeyFn(key);

    // 1. Якщо увімкнено кеш і ключ уже запитувався — повертаємо готовий Promise
    if (this.useCache) {
      const cached = this.cacheMap.get(cacheKey);
      if (cached !== undefined) {
        return cached;
      }
    }

    // 2. Створюємо новий Promise і додаємо його в чергу відкладеного виконання
    const promise = new Promise<V>((resolve, reject) => {
      this.queue.push({ key, resolve, reject });

      // Якщо черга досягла максимального розміру — скидаємо негайно
      if (this.queue.length >= this.maxBatchSize) {
        this.dispatchQueue();
      } else if (!this.batchScheduled) {
        // Плануємо скидання черги на наступний такт мікротасок
        this.batchScheduled = true;
        queueMicrotask(() => this.dispatchQueue());
      }
    });

    if (this.useCache) {
      this.cacheMap.set(cacheKey, promise);
    }

    return promise;
  }

  public loadMany(keys: ReadonlyArray<K>): Promise<Array<V | Error>> {
    return Promise.all(
      keys.map((key) => this.load(key).catch((err: Error) => err))
    );
  }

  public clear(key: K): this {
    const cacheKey = this.cacheKeyFn(key);
    this.cacheMap.delete(cacheKey);
    return this;
  }

  public clearAll(): this {
    this.cacheMap.clear();
    return this;
  }

  public prime(key: K, value: V | Error): this {
    const cacheKey = this.cacheKeyFn(key);
    if (!this.cacheMap.has(cacheKey)) {
      const promise = value instanceof Error 
        ? Promise.reject(value) 
        : Promise.resolve(value);
      // Запобігаємо unhandled rejection для помилок у кеші
      promise.catch(() => {});
      this.cacheMap.set(cacheKey, promise);
    }
    return this;
  }

  private async dispatchQueue(): Promise<void> {
    this.batchScheduled = false;
    const currentQueue = this.queue;
    this.queue = [];

    if (currentQueue.length === 0) return;

    const keys = currentQueue.map((item) => item.key);

    try {
      // Викликаємо користувацьку пакетну функцію
      const values = await this.batchFn(keys);

      // Перевіряємо суворий інваріант контракту DataLoader
      if (values.length !== keys.length) {
        throw new TypeError(
          `DataLoader batch function must return array of length ${keys.length}, but got ${values.length}`
        );
      }

      // Розподіляємо значення по індивідуальних промісах
      for (let i = 0; i < currentQueue.length; i++) {
        const result = values[i];
        if (result instanceof Error) {
          currentQueue[i].reject(result);
        } else {
          currentQueue[i].resolve(result);
        }
      }
    } catch (error) {
      // Якщо впала вся пакетна функція — відхиляємо всі проміси поточного пакета
      const err = error instanceof Error ? error : new Error(String(error));
      for (const item of currentQueue) {
        item.reject(err);
      }
    }
  }
}
