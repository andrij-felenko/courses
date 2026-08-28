// TypeScript: Клієнтська черга вихідних мутацій з оптимістичним станом

export type MutationType = 'CREATE' | 'UPDATE' | 'DELETE';
export type MutationStatus = 'PENDING' | 'IN_FLIGHT' | 'COMMITTED' | 'FAILED';

export interface Mutation<T = unknown> {
  id: string;              // Унікальний UUID для ідемпотентності на сервері
  entityId: string;        // Ідентифікатор цільової сутності
  entityType: string;      // Тип сутності (наприклад, 'notes', 'tasks')
  type: MutationType;      // Тип операції
  payload: T;              // Дані для застосування (або дельта)
  baseVersion: number;     // Версія сутності, яку бачив клієнт при створенні мутації
  createdAt: number;       // Локальна часова мітка створення
  status: MutationStatus;  // Поточний статус у життєвому циклі
  retryCount: number;      // Кількість невдалих спроб відправки
}

export interface EntityState {
  id: string;
  version: number;
  data: Record<string, unknown>;
  isOptimistic?: boolean;  // Прапорець для UI: стан ще не підтверджено сервером
}

export interface StorageDriver {
  saveMutation(mutation: Mutation): Promise<void>;
  deleteMutation(id: string): Promise<void>;
  getPendingMutations(): Promise<Mutation[]>;
  saveEntity(entity: EntityState): Promise<void>;
  getEntity(id: string): Promise<EntityState | null>;
}

export class DurableMutationQueue {
  private isProcessing = false;
  private syncTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    private readonly storage: StorageDriver,
    private readonly networkSender: (mutation: Mutation) => Promise<{ success: boolean; newVersion?: number; errorCode?: number }>
  ) {}

  /**
   * Атомарне додавання мутації: збереження в Outbox та оптимістичне оновлення стану
   */
  async enqueue<T extends Record<string, unknown>>(
    entityId: string,
    entityType: string,
    type: MutationType,
    payload: T
  ): Promise<void> {
    const current = (await this.storage.getEntity(entityId)) ?? {
      id: entityId,
      version: 0,
      data: {}
    };

    const mutation: Mutation<T> = {
      id: crypto.randomUUID(),
      entityId,
      entityType,
      type,
      payload,
      baseVersion: current.version,
      createdAt: Date.now(),
      status: 'PENDING',
      retryCount: 0
    };

    // 1. Зберігаємо мутацію в чергу на диску
    await this.storage.saveMutation(mutation);

    // 2. Оптимістично застосовуємо зміни до локальної копії сутності
    const optimisticData = { ...current.data, ...payload };
    await this.storage.saveEntity({
      id: entityId,
      version: current.version, // Базова версія не змінюється до підтвердження сервером
      data: optimisticData,
      isOptimistic: true
    });

    // 3. Ініціюємо спробу відправки
    this.scheduleProcessing(0);
  }

  /**
   * Планування обробки черги з розрахунком випадкового джитеру
   */
  private scheduleProcessing(delayMs: number): void {
    if (this.syncTimer) clearTimeout(this.syncTimer);
    this.syncTimer = setTimeout(() => {
      void this.processQueue();
    }, delayMs);
  }

  /**
   * Конвеєр вивантаження черги мутацій
   */
  async processQueue(): Promise<void> {
    if (this.isProcessing) return;
    this.isProcessing = true;

    try {
      const pending = await this.storage.getPendingMutations();
      // Сортуємо впорядковано за часом створення (FIFO для однієї сутності)
      pending.sort((a, b) => a.createdAt - b.createdAt);

      for (const mutation of pending) {
        mutation.status = 'IN_FLIGHT';
        await this.storage.saveMutation(mutation);

        try {
          const response = await this.networkSender(mutation);

          if (response.success && response.newVersion !== undefined) {
            // Сервер успішно зафіксував мутацію
            const entity = await this.storage.getEntity(mutation.entityId);
            if (entity) {
              entity.version = response.newVersion;
              entity.isOptimistic = false;
              await this.storage.saveEntity(entity);
            }
            // Видаляємо підтверджену дію з черги
            await this.storage.deleteMutation(mutation.id);
          } else if (response.errorCode && response.errorCode >= 400 && response.errorCode < 500) {
            // Непоправна бізнес-помилка або конфлікт валідації -> Відкат оптимізму
            console.error(`Мутація ${mutation.id} відхилена сервером (код ${response.errorCode}). Відкат.`);
            await this.rollbackMutation(mutation);
            await this.storage.deleteMutation(mutation.id);
          } else {
            // Тимчасова серверна помилка (5xx) або таймаут -> Експоненційний відступ
            await this.handleRetry(mutation);
            break; // Зупиняємо конвеєр черги до наступного інтервалу
          }
        } catch {
          // Мережевий обрив
          await this.handleRetry(mutation);
          break;
        }
      }
    } finally {
      this.isProcessing = false;
    }
  }

  private async handleRetry(mutation: Mutation): Promise<void> {
    mutation.status = 'PENDING';
    mutation.retryCount += 1;
    await this.storage.saveMutation(mutation);

    // Розрахунок Full Jitter: pause = random(0, min(max_backoff, base * 2^retries))
    const baseBackoffMs = 500;
    const maxBackoffMs = 30000;
    const temp = Math.min(maxBackoffMs, baseBackoffMs * Math.pow(2, mutation.retryCount));
    const jitterDelay = Math.floor(Math.random() * temp);

    this.scheduleProcessing(jitterDelay);
  }

  private async rollbackMutation(mutation: Mutation): Promise<void> {
    const entity = await this.storage.getEntity(mutation.entityId);
    if (!entity) return;

    // Відкат: повертаємо стан до неоптимістичного (або перезавантажуємо базовий знімок)
    entity.isOptimistic = false;
    await this.storage.saveEntity(entity);
  }
}
