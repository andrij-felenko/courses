// Стандартизовані коди помилок канонічного контракту
export type DeviceErrorCode =
  | 'DEVICE_UNREACHABLE'
  | 'HARDWARE_INVARIANT_VIOLATION'
  | 'COMMAND_TIMEOUT'
  | 'RATE_LIMIT_EXCEEDED'
  | 'RECONCILIATION_FAILED';

// Структура типізованої помилки
export interface CanonicalDeviceError {
  code: DeviceErrorCode;
  message: string;
  deviceId: string;
  capability?: string;
  // Додаткові параметри для локалізації та інженерної діагностики
  details?: Record<string, unknown>;
  timestamp: string;
}

// Модель роздільного представлення бажаного та фактичного станів
export interface ReconciledDeviceState {
  deviceId: string;
  // Стан, підтверджений радіопакетами від фізичного обладнання
  reportedState: Record<string, unknown>;
  // Бажаний стан, запропонований командами користувача чи автоматизацій
  desiredState: Record<string, unknown>;
  // Чи триває наразі процес фізичного застосування змін
  isReconciling: boolean;
  // Остання зафіксована помилка узгодження
  lastError?: CanonicalDeviceError;
}

// Валідатор апаратних інваріантів перед надсиланням команди в ефір
export function validateHardwareInvariants(
  capability: string,
  value: Record<string, unknown>
): CanonicalDeviceError | null {
  // Інваріант безпеки: обмеження максимальної температури теплої підлоги
  if (capability === 'target_temperature') {
    const temp = value.celsius as number;
    if (temp < 5 || temp > 35) {
      return {
        code: 'HARDWARE_INVARIANT_VIOLATION',
        message: 'Цільова температура виходить за межі безпечного діапазону 5..35 °C',
        deviceId: 'validator',
        capability: capability,
        details: { requestedCelsius: temp, min: 5, max: 35 },
        timestamp: new Date().toISOString(),
      };
    }
  }

  return null;
}
