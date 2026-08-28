/**
 * Диспетчер оптимістичних мутацій на TypeScript
 */

export interface Entity {
  id: string;
  title: string;
  completed: boolean;
  parentId?: string;
}

export interface State {
  entities: Record<string, Entity>;
}

export type MutationType = 'CREATE' | 'UPDATE' | 'DELETE';

export interface Mutation {
  id: string;              // Унікальний ID операції (UUID / Idempotency Key)
  type: MutationType;
  entityId: string;        // Цільовий ID сутності (може бути temp-id)
  tempId?: string;         // Якщо створюється нова сутність
  payload: Partial<Entity>;
  timestamp: number;
  abortController: AbortController;
  retries: number;
}

export interface ServerResponse {
  success: boolean;
  tempId?: string;
  serverId?: string;
  data?: Partial<Entity>;
  error?: { status: number; message: string };
}

export class OptimisticMutationManager {
  private canonicalState: State;
  private pendingQueue: Mutation[] = [];
  private idMap: Map<string, string> = new Map(); // tempId -> serverId
  private listeners: Array<(state: State) => void> = [];

  constructor(initialState: State = { entities: {} }) {
    this.canonicalState = JSON.parse(JSON.stringify(initialState));
  }

  /**
   * Підписка на оновлення стану подання (View State)
   */
  public subscribe(listener: (state: State) => void): () => void {
    this.listeners.push(listener);
    listener(this.getViewState());
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notify(): void {
    const state = this.getViewState();
    for (const listener of this.listeners) {
      listener(state);
    }
  }

  /**
   * Чистий редуктор: застосовує одну мутацію до стану
   */
  private applyMutation(state: State, mutation: Mutation): State {
    const nextState: State = {
      entities: { ...state.entities }
    };

    // Трансляція ID якщо сутність посилається на замінений temp-id
    const targetId = this.resolveId(mutation.entityId);
    const resolvedParentId = mutation.payload.parentId
      ? this.resolveId(mutation.payload.parentId)
      : undefined;

    switch (mutation.type) {
      case 'CREATE': {
        const id = mutation.tempId || targetId;
        nextState.entities[id] = {
          id,
          title: mutation.payload.title || '',
          completed: mutation.payload.completed || false,
          ...(resolvedParentId ? { parentId: resolvedParentId } : {})
        };
        break;
      }
      case 'UPDATE': {
        if (nextState.entities[targetId]) {
          nextState.entities[targetId] = {
            ...nextState.entities[targetId],
            ...mutation.payload,
            id: targetId,
            ...(resolvedParentId ? { parentId: resolvedParentId } : {})
          };
        }
        break;
      }
      case 'DELETE': {
        delete nextState.entities[targetId];
        break;
      }
    }

    return nextState;
  }

  /**
   * Обчислення View State як згортки черги поверх канонічного стану
   */
  public getViewState(): State {
    return this.pendingQueue.reduce(
      (state, mut) => this.applyMutation(state, mut),
      this.canonicalState
    );
  }

  public resolveId(id: string): string {
    return this.idMap.get(id) || id;
  }

  /**
   * Додавання нової оптимістичної дії
   */
  public async dispatch(
    type: MutationType,
    entityId: string,
    payload: Partial<Entity>,
    networkExecutor: (mut: Mutation, signal: AbortSignal) => Promise<ServerResponse>
  ): Promise<void> {
    const mutationId = `mut_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    const tempId = type === 'CREATE' ? entityId : undefined;
    const abortController = new AbortController();

    // Скасовуємо попередні незавершені мутації ДЛЯ ТІЄЇ САМОЇ СУТНОСТІ (захист від гонок)
    for (const prev of this.pendingQueue) {
      if (this.resolveId(prev.entityId) === this.resolveId(entityId) && prev.type === 'UPDATE') {
        prev.abortController.abort();
      }
    }

    const mutation: Mutation = {
      id: mutationId,
      type,
      entityId,
      tempId,
      payload,
      timestamp: Date.now(),
      abortController,
      retries: 0
    };

    // 1. Оптимістично додаємо в чергу
    this.pendingQueue.push(mutation);
    this.notify(); // UI оновлюється миттєво (<1 мс)

    // 2. Асинхронно відправляємо в мережу
    await this.executeMutation(mutation, networkExecutor);
  }

  private async executeMutation(
    mutation: Mutation,
    networkExecutor: (mut: Mutation, signal: AbortSignal) => Promise<ServerResponse>
  ): Promise<void> {
    try {
      // Підміняємо payload актуальними ID перед виходом у мережу
      const currentMutation: Mutation = {
        ...mutation,
        entityId: this.resolveId(mutation.entityId),
        payload: {
          ...mutation.payload,
          parentId: mutation.payload.parentId ? this.resolveId(mutation.payload.parentId) : undefined
        }
      };

      const response = await networkExecutor(currentMutation, mutation.abortController.signal);

      if (response.success) {
        this.handleSuccess(mutation, response);
      } else {
        this.handleFailure(mutation, response.error, networkExecutor);
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        // Запит було скасовано новішою мутацією — просто прибираємо з черги
        this.pendingQueue = this.pendingQueue.filter(m => m.id !== mutation.id);
        return;
      }
      // Мережевий таймаут або розрив з'єднання — переводимо в режим повтору
      this.handleNetworkError(mutation, networkExecutor);
    }
  }

  private handleSuccess(mutation: Mutation, res: ServerResponse): void {
    // Якщо створювали нову сутність і сервер повернув канонічний ID
    if (mutation.tempId && res.serverId) {
      this.idMap.set(mutation.tempId, res.serverId);
      // Оновлюємо посилання в канонічному та всіх очікуючих мутаціях
      mutation.entityId = res.serverId;
    }

    // 1. Фіксуємо зміну в канонічному стані сервера
    this.canonicalState = this.applyMutation(this.canonicalState, mutation);

    // 2. Видаляємо виконану мутацію з черги pending
    this.pendingQueue = this.pendingQueue.filter(m => m.id !== mutation.id);

    // 3. Сповіщаємо UI (згортка тепер спирається на оновлений канонічний стан)
    this.notify();
  }

  private handleFailure(
    mutation: Mutation,
    error: { status: number; message: string } | undefined,
    networkExecutor: (mut: Mutation, signal: AbortSignal) => Promise<ServerResponse>
  ): void {
    const status = error?.status || 500;

    // Фатальні помилки валідації або доступу (4xx окрім 408/429) -> REBASE ROLLBACK
    if (status >= 400 && status < 500 && status !== 408 && status !== 429) {
      console.warn(`[OptimisticManager] Fatal mutation failure (${status}): ${error?.message}`);
      // Видаляємо збійну мутацію з черги. Решта мутацій лишаються!
      this.pendingQueue = this.pendingQueue.filter(m => m.id !== mutation.id);
      this.notify(); // Rebase: UI автоматично перераховується без цієї дії
      return;
    }

    // Тимчасові помилки бекенда (5xx, 429) -> Повтор
    this.handleNetworkError(mutation, networkExecutor);
  }

  private handleNetworkError(
    mutation: Mutation,
    networkExecutor: (mut: Mutation, signal: AbortSignal) => Promise<ServerResponse>
  ): void {
    mutation.retries += 1;
    const maxRetries = 4;

    if (mutation.retries <= maxRetries) {
      const delayMs = Math.min(1000 * Math.pow(2, mutation.retries), 10000);
      console.log(`[OptimisticManager] Scheduling retry #${mutation.retries} in ${delayMs}ms`);
      setTimeout(() => {
        if (this.pendingQueue.some(m => m.id === mutation.id)) {
          this.executeMutation(mutation, networkExecutor);
        }
      }, delayMs);
    } else {
      // Вичерпано спроби — відкат за перебазуванням
      this.pendingQueue = this.pendingQueue.filter(m => m.id !== mutation.id);
      this.notify();
    }
  }
}
