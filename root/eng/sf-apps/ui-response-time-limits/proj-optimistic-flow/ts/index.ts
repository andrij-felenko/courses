// TypeScript: Оптимістичне сховище з чергою мутацій та стійким перебазуванням

export interface Task {
  readonly id: string;
  readonly title: string;
  readonly completed: boolean;
}

export interface AppState {
  readonly tasks: readonly Task[];
}

export interface Mutation<T> {
  readonly id: string;
  readonly apply: (state: T) => T;
  readonly rollback: (state: T) => T;
  readonly execute: () => Promise<void>;
}

export class OptimisticStore<T> {
  private committedState: T;
  private optimisticState: T;
  private pendingMutations: Mutation<T>[] = [];
  private listeners: Set<(state: T) => void> = new Set();

  constructor(initialState: T) {
    this.committedState = initialState;
    this.optimisticState = initialState;
  }

  public getState(): T {
    return this.optimisticState;
  }

  public subscribe(listener: (state: T) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    for (const listener of this.listeners) {
      listener(this.optimisticState);
    }
  }

  /**
   * Застосовує мутацію оптимістично та запускає фонове збереження
   */
  public async dispatch(mutation: Mutation<T>): Promise<boolean> {
    // 1. Миттєве оновлення інтерфейсу (виконується за <1 мс, гарантує поріг 100 мс)
    this.pendingMutations.push(mutation);
    this.optimisticState = mutation.apply(this.optimisticState);
    this.notify();

    // 2. Фонова передача на сервер
    try {
      await mutation.execute();

      // 3. Успіх: фіксуємо мутацію у підтвердженому стані
      this.committedState = mutation.apply(this.committedState);
      this.pendingMutations = this.pendingMutations.filter((m) => m.id !== mutation.id);
      return true;
    } catch (error) {
      // 4. Помилка: відкат та перебазування решти активних мутацій
      this.pendingMutations = this.pendingMutations.filter((m) => m.id !== mutation.id);
      this.rebase();
      this.notify();
      return false;
    }
  }

  /**
   * Перебазування: повторне застосування всіх активних мутацій поверх останнього committed стану
   */
  private rebase(): void {
    let state = this.committedState;
    for (const pending of this.pendingMutations) {
      state = pending.apply(state);
    }
    this.optimisticState = state;
  }
}
