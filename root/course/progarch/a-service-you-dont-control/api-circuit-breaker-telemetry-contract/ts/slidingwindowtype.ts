export type SlidingWindowType = 'COUNT_BASED' | 'TIME_BASED';

export interface CircuitBreakerConfig {
  // Тип та розмір аналітичного ковзного вікна
  readonly slidingWindowType: SlidingWindowType;
  readonly slidingWindowSize: number;

  // Поріг активації розрахунку частки відмов
  readonly minimumNumberOfCalls: number;

  // Порогові критерії збоїв та повільних викликів (у відсотках)
  readonly failureRateThreshold: number;      // Наприклад: 50.0 (%)
  readonly slowCallRateThreshold: number;     // Наприклад: 60.0 (%)
  readonly slowCallDurationThresholdMs: number; // Наприклад: 2000 (мс)

  // Параметри охолодження та зондування
  readonly waitDurationInOpenStateMs: number;
  readonly permittedNumberOfCallsInHalfOpenState: number;

  // Автоматичний перехід у HALF_OPEN після вичерпання таймера (true)
  // чи лінивий перехід під час надходження першого запиту (false)
  readonly automaticTransitionFromOpenToHalfOpenEnabled: boolean;

  // Фільтрація типів помилок для реєстрації
  readonly ignoredExceptions?: string[];
  readonly recordedExceptions?: string[];
}
