// 1. Повна множина станів автомата запобіжника
export type CircuitBreakerState =
  | 'CLOSED'
  | 'OPEN'
  | 'HALF_OPEN'
  | 'FORCED_OPEN'
  | 'FORCED_CLOSED'
  | 'DISABLED';

// 2. Типізовані причини переходу між станами
export type TransitionReason =
  | 'FAILURE_RATE_EXCEEDED'
  | 'SLOW_CALL_RATE_EXCEEDED'
  | 'WAIT_DURATION_EXPIRED'
  | 'PROBE_CALLS_SUCCEEDED'
  | 'PROBE_CALLS_FAILED'
  | 'ADMIN_FORCE_OPEN'
  | 'ADMIN_FORCE_CLOSE'
  | 'ADMIN_RESET';

// 3. Структурована подія переходу стану (StateTransitionEvent)
export interface StateTransitionEvent {
  readonly breakerName: string;
  readonly fromState: CircuitBreakerState;
  readonly toState: CircuitBreakerState;
  readonly reason: TransitionReason;
  readonly timestamp: Date;
  readonly currentFailureRatePct: number;
  readonly currentSlowCallRatePct: number;
}

// 4. Програмний контракт інтерфейсу автомата станів
export interface CircuitBreakerStateMachine {
  readonly name: string;
  readonly state: CircuitBreakerState;

  // Перевірка дозволу на виконання запиту перед відправленням у мережу
  tryAcquirePermission(): boolean;

  // Фіксація результату виконання для оновлення метрик і перевірки переходів
  onSuccess(durationMs: number): void;
  onError(durationMs: number, error: unknown): void;

  // Адміністративні методи примусового перемикання станів
  forceOpen(): void;
  forceClose(): void;
  reset(): void;

  // Підписка на події зміни стану для систем телеметрії та аудиту
  onStateTransition(listener: (event: StateTransitionEvent) => void): void;
}
