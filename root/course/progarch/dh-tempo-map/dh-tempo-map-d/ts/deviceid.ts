// Типи канонічних команд та подій, визначені контрактом ядра
export type DeviceId = string;
export type PowerState = 'ON' | 'OFF';

export interface CommandDispatchResult {
  readonly commandId: string;
  readonly deviceId: DeviceId;
  readonly targetState: PowerState;
}

export interface DeviceStateChangedEvent {
  readonly type: 'DEVICE_STATE_CHANGED';
  readonly deviceId: DeviceId;
  readonly actualState: PowerState;
  readonly correlationId?: string;
}

export interface DeviceCommandFailedEvent {
  readonly type: 'DEVICE_COMMAND_FAILED';
  readonly commandId: string;
  readonly deviceId: DeviceId;
  readonly faultCode: 'RELAY_COIL_BURNOUT' | 'OVERCURRENT_TRIP' | 'TIMEOUT';
  readonly message: string;
}

export type InboundBusEvent = DeviceStateChangedEvent | DeviceCommandFailedEvent;

// Інтерфейс відправки команд у буферну шину ядра
export interface ICommandBus {
  sendCommand(deviceId: DeviceId, targetState: PowerState): Promise<string>;
}

// Запис про незавершену оптимістичну дію
interface PendingOptimisticAction {
  readonly commandId: string;
  readonly deviceId: DeviceId;
  readonly previousState: PowerState;
  readonly optimisticState: PowerState;
  readonly timeoutHandle: ReturnType<typeof setTimeout>;
}

// Слухач змін для оновлення візуальних компонентів
export type StateChangeListener = (
  deviceId: DeviceId,
  state: PowerState,
  errorMessage?: string
) => void;

export class OptimisticDeviceStore {
  private readonly authoritativeStates = new Map<DeviceId, PowerState>();
  private readonly pendingActions = new Map<string, PendingOptimisticAction>();
  private readonly listeners = new Set<StateChangeListener>();

  constructor(
    private readonly commandBus: ICommandBus,
    private readonly timeoutMs: number = 2000
  ) {}

  public subscribe(listener: StateChangeListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  public getDeviceState(deviceId: DeviceId): PowerState {
    return this.authoritativeStates.get(deviceId) ?? 'OFF';
  }

  // Ініціалізація початкового стану пристрою з кешу ядра
  public initializeDevice(deviceId: DeviceId, state: PowerState): void {
    this.authoritativeStates.set(deviceId, state);
    this.notifyListeners(deviceId, state);
  }

  // Виклик з боку UI: миттєва оптимістична зміна та відправка команди
  public async toggleSwitch(deviceId: DeviceId, targetState: PowerState): Promise<void> {
    const previousState = this.getDeviceState(deviceId);
    if (previousState === targetState) {
      return;
    }

    // 1. Оптимістично застосовуємо новий стан на екрані
    this.authoritativeStates.set(deviceId, targetState);
    this.notifyListeners(deviceId, targetState);

    try {
      // 2. Відправляємо команду в буферну шину та отримуємо ідентифікатор кореляції
      const commandId = await this.commandBus.sendCommand(deviceId, targetState);

      // 3. Встановлюємо таймер очікування підтвердження від апаратури
      const timeoutHandle = setTimeout(() => {
        this.handleTimeout(commandId);
      }, this.timeoutMs);

      this.pendingActions.set(commandId, {
        commandId,
        deviceId,
        previousState,
        optimisticState: targetState,
        timeoutHandle,
      });
    } catch (networkError) {
      // Якщо шина взагалі недосяжна, відкочуємося негайно
      this.authoritativeStates.set(deviceId, previousState);
      const message = networkError instanceof Error ? networkError.message : 'Збій шини';
      this.notifyListeners(deviceId, previousState, `Не вдалося надіслати команду: ${message}`);
    }
  }

  // Обробник висхідних подій з буферної шини Pub/Sub
  public handleInboundEvent(event: InboundBusEvent): void {
    if (event.type === 'DEVICE_COMMAND_FAILED') {
      this.reconcileFailure(event);
    } else if (event.type === 'DEVICE_STATE_CHANGED') {
      this.reconcileStateChange(event);
    }
  }

  private reconcileFailure(event: DeviceCommandFailedEvent): void {
    const action = this.pendingActions.get(event.commandId);
    if (!action) {
      return;
    }

    clearTimeout(action.timeoutHandle);
    this.pendingActions.delete(event.commandId);

    // Відкат до дійсного стану через апаратний збій
    this.authoritativeStates.set(action.deviceId, action.previousState);
    this.notifyListeners(
      action.deviceId,
      action.previousState,
      `Апаратна помилка [${event.faultCode}]: ${event.message}`
    );
  }

  private reconcileStateChange(event: DeviceStateChangedEvent): void {
    if (event.correlationId) {
      const action = this.pendingActions.get(event.correlationId);
      if (action) {
        clearTimeout(action.timeoutHandle);
        this.pendingActions.delete(event.correlationId);
      }
    }

    // Авторитетне оновлення стану (підтвердження або спонтанна зміна від заліза)
    this.authoritativeStates.set(event.deviceId, event.actualState);
    this.notifyListeners(event.deviceId, event.actualState);
  }

  private handleTimeout(commandId: string): void {
    const action = this.pendingActions.get(commandId);
    if (!action) {
      return;
    }

    this.pendingActions.delete(commandId);
    // Відкат через відсутність своєчасної відповіді від заліза
    this.authoritativeStates.set(action.deviceId, action.previousState);
    this.notifyListeners(
      action.deviceId,
      action.previousState,
      'Тайм-аут: пристрій не відповів у встановлений термін'
    );
  }

  private notifyListeners(deviceId: DeviceId, state: PowerState, error?: string): void {
    for (const listener of this.listeners) {
      listener(deviceId, state, error);
    }
  }
}
