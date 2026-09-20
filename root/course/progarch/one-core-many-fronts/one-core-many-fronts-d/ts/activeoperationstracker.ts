// Контракт зупинки драйвуючого адаптера
export interface DrivingAdapter {
  readonly name: string;
  stop(): Promise<void>;
}

// Контракт керованого адаптера сховища або зовнішнього з'єднання
export interface DisposableResource {
  readonly name: string;
  close(): Promise<void>;
}

// Відстежувач активних операцій усередині прикладного ядра
export class ActiveOperationsTracker {
  private activeCount = 0;
  private drainResolve: (() => void) | null = null;

  track<T>(operation: () => Promise<T>): Promise<T> {
    this.activeCount++;
    return operation().finally(() => {
      this.activeCount--;
      if (this.activeCount === 0 && this.drainResolve) {
        this.drainResolve();
        this.drainResolve = null;
      }
    });
  }

  get count(): number {
    return this.activeCount;
  }

  async waitForDrain(timeoutMs: number): Promise<boolean> {
    if (this.activeCount === 0) {
      return true;
    }

    return new Promise<boolean>((resolve) => {
      const timer = setTimeout(() => {
        this.drainResolve = null;
        resolve(false);
      }, timeoutMs);

      this.drainResolve = () => {
        clearTimeout(timer);
        resolve(true);
      };
    });
  }
}

// Координована узгоджена зупинка в композиційному корені
export async function gracefulShutdown(
  adapters: readonly DrivingAdapter[],
  tracker: ActiveOperationsTracker,
  resources: readonly DisposableResource[],
  timeoutMs = 10_000
): Promise<number> {
  // Фаза 1: закриття мережевих сокетів і зупинка читання з черг
  await Promise.allSettled(
    adapters.map(async (adapter) => {
      try {
        await adapter.stop();
      } catch (err) {
        console.error(`Збій під час зупинки адаптера ${adapter.name}:`, err);
      }
    })
  );

  // Фаза 2: очікування завершення активних прикладних сценаріїв
  const drained = await tracker.waitForDrain(timeoutMs);

  // Фаза 3: закриття з'єднань із базами даних та вивільнення дескрипторів
  let hasErrors = !drained;
  for (const resource of resources) {
    try {
      await resource.close();
    } catch (err) {
      console.error(`Збій під час закриття ресурсу ${resource.name}:`, err);
      hasErrors = true;
    }
  }

  return hasErrors ? 1 : 0;
}
