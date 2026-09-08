// Контракт команди оперативного керування
export interface AdminCommandRequest {
  readonly operatorId: string; // Ідентифікатор чергового інженера
  readonly ticketId: string;   // Номер інциденту в Jira / PagerDuty
  readonly reason: string;     // Текстове інженерне обґрунтування дії
  readonly durationMinutes?: number; // Опціональний таймаут автоскасування блокування
}

// Результат виконання адміністративної команди
export interface AdminCommandResponse {
  readonly name: string;
  readonly previousState: CircuitBreakerState;
  readonly currentState: CircuitBreakerState;
  readonly message: string;
  readonly timestamp: string;
}

// Контракт сервісу оперативного керування запобіжниками
export interface CircuitBreakerRegistryService {
  getBreakerOverview(): Array<{ name: string; state: CircuitBreakerState; isForced: boolean }>;
  getBreakerDetails(name: string): Record<string, unknown>;
  forceOpen(name: string, command: AdminCommandRequest): AdminCommandResponse;
  forceClosed(name: string, command: AdminCommandRequest): AdminCommandResponse;
  reset(name: string, command: AdminCommandRequest): AdminCommandResponse;
}

// Реалізація контролера адміністративного API
export class CircuitBreakerAdminController {
  constructor(
    private readonly registry: CircuitBreakerRegistryService,
    private readonly auditLogger: (entry: Record<string, unknown>) => void
  ) {}

  // Обробник отримання деталей стану запобіжника
  public handleGetDetails(name: string): { status: number; body: unknown } {
    try {
      const details = this.registry.getBreakerDetails(name);
      return { status: 200, body: details };
    } catch (error) {
      return { status: 404, body: { error: `Circuit breaker '${name}' not found` } };
    }
  }

  // Примусове розмикання контуру черговим інженером
  public handleForceOpen(name: string, request: AdminCommandRequest): { status: number; body: unknown } {
    this.validateAdminRequest(request);

    const result = this.registry.forceOpen(name, request);

    // Обов'язкова реєстрація події в системному аудит-лозі
    this.auditLogger({
      eventType: 'CIRCUIT_BREAKER_FORCED_OPEN',
      circuitBreaker: name,
      operatorId: request.operatorId,
      ticketId: request.ticketId,
      reason: request.reason,
      previousState: result.previousState,
      currentState: result.currentState,
      timestamp: result.timestamp,
    });

    return { status: 200, body: result };
  }

  // Примусове замикання контуру (аварійний байпас)
  public handleForceClosed(name: string, request: AdminCommandRequest): { status: number; body: unknown } {
    this.validateAdminRequest(request);

    const result = this.registry.forceClosed(name, request);

    this.auditLogger({
      eventType: 'CIRCUIT_BREAKER_FORCED_CLOSED',
      circuitBreaker: name,
      operatorId: request.operatorId,
      ticketId: request.ticketId,
      reason: request.reason,
      previousState: result.previousState,
      currentState: result.currentState,
      timestamp: result.timestamp,
    });

    return { status: 200, body: result };
  }

  // Безпечне скидання статистики та повернення до автоматичного режиму
  public handleReset(name: string, request: AdminCommandRequest): { status: number; body: unknown } {
    this.validateAdminRequest(request);

    const result = this.registry.reset(name, request);

    this.auditLogger({
      eventType: 'CIRCUIT_BREAKER_RESET',
      circuitBreaker: name,
      operatorId: request.operatorId,
      ticketId: request.ticketId,
      reason: request.reason,
      previousState: result.previousState,
      currentState: result.currentState,
      timestamp: result.timestamp,
    });

    return { status: 200, body: result };
  }

  // Валідація обов'язкових полів операторського запиту
  private validateAdminRequest(request: AdminCommandRequest): void {
    if (!request.operatorId || request.operatorId.trim().length === 0) {
      throw new Error('Validation failed: operatorId is required for audit');
    }
    if (!request.ticketId || request.ticketId.trim().length === 0) {
      throw new Error('Validation failed: ticketId is required for incident tracking');
    }
    if (!request.reason || request.reason.trim().length === 0) {
      throw new Error('Validation failed: explanation reason is required');
    }
  }
}
