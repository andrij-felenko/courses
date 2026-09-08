export interface StateTransitionEvent {
  // Назва конкретного екземпляра запобіжника
  readonly circuitBreakerName: string;

  // Попередній та новий стани автомата
  readonly fromState: CircuitBreakerState;
  readonly toState: CircuitBreakerState;

  // Точна причина переходу
  readonly transitionReason: TransitionReason;

  // Часова мітка у форматі ISO 8601 UTC
  readonly timestamp: string;

  // Миттєвий знімок метрик ковзного вікна на момент ухвалення рішення
  readonly metricsSnapshot: {
    readonly failureRatePercentage: number;
    readonly slowCallRatePercentage: number;
    readonly totalBufferedCalls: number;
    readonly failedCallsCount: number;
    readonly slowCallsCount: number;
  };

  // Джерело переходу: спрацювання автоматики чи дія людини
  readonly triggeredBy: 'AUTOMATIC_THRESHOLD' | 'ADMIN_CONTROL_PLANE' | 'TIMER_EXPIRY';
}
