/**
 * config/options.js — Декларативні сценарії навантаження k6 та пороги SLA (Thresholds).
 * Формалізує вимоги контракту до продуктивності, затримок та відсотка відмов.
 */

// Базова конфігурація цільового середовища з можливістю перевизначення через CLI:
// k6 run -e TARGET_URL=https://staging.internal -e SCENARIO=load main.js
const env = typeof __ENV !== 'undefined' ? __ENV : (typeof process !== 'undefined' ? process.env : {});
export const TARGET_URL = env.TARGET_URL || 'http://127.0.0.1:8080';
export const SELECTED_SCENARIO = env.SCENARIO || 'smoke';

/**
 * Контрактні пороги якості (SLA Thresholds) для автоматичного блокування приймання (Acceptance Gate).
 * Якщо хоча б один поріг порушено, k6 завершує виконання з кодом помилки (exit code != 0).
 */
export const thresholds = {
  // Загальний відсоток помилкових HTTP-відповідей не має перевищувати 1%
  http_req_failed: [
    { threshold: 'rate<0.01', abortOnFail: true, delayAbortEval: '10s' },
  ],
  // 95-й процентиль часу відповіді HTTP має бути меншим за 400 мс, 99-й — меншим за 800 мс
  http_req_duration: ['p(95)<400', 'p(99)<800'],
  // Кастомна метрика тривалості наскрізної бізнес-транзакції створення замовлення
  business_transaction_duration: ['p(95)<500', 'max<1500'],
  // Усі контрактні перевірки (Checks) повинні мати успішність не менше 99%
  contract_checks_success: ['rate>0.99'],
};

/**
 * Профілі навантаження, що моделюють різні експлуатаційні режими системи.
 */
export const allScenarios = {
  // 1. Димове тестування (Smoke): перевірка базової працездатності під мінімальним навантаженням
  smoke: {
    executor: 'shared-iterations',
    vus: 1,
    iterations: 15,
    maxDuration: '1m',
    gracefulStop: '5s',
    tags: { test_type: 'smoke' },
  },

  // 2. Цільове контрактне навантаження (Load): емуляція узгодженого в SLA потоку запитів
  load: {
    executor: 'ramping-arrival-rate',
    startRate: 10,
    timeUnit: '1s',
    preAllocatedVUs: 30,
    maxVUs: 150,
    stages: [
      { target: 30, duration: '1m' }, // Плавний розгін (Ramp-up)
      { target: 30, duration: '3m' }, // Робоче плато номінального навантаження
      { target: 0, duration: '30s' }, // Зниження навантаження (Ramp-down)
    ],
    tags: { test_type: 'load' },
  },

  // 3. Стрес-тестування (Stress): пошук точки відмови та перевірка граційного деградування
  stress: {
    executor: 'ramping-arrival-rate',
    startRate: 20,
    timeUnit: '1s',
    preAllocatedVUs: 50,
    maxVUs: 300,
    stages: [
      { target: 50, duration: '1m' },
      { target: 100, duration: '2m' }, // Перевищення номіналу в 3 рази
      { target: 150, duration: '2m' }, // Пошук межі пропускної здатності
      { target: 0, duration: '1m' },
    ],
    tags: { test_type: 'stress' },
  },

  // 4. Тест на витривалість (Soak): виявлення витоків пам'яті та деградації пулів з'єднань
  soak: {
    executor: 'constant-arrival-rate',
    rate: 25,
    timeUnit: '1s',
    duration: '30m',
    preAllocatedVUs: 40,
    maxVUs: 100,
    tags: { test_type: 'soak' },
  },
};

/**
 * Експортований об'єкт options для k6.
 * Обирає вказаний через SCENARIO профіль або активує smoke за замовчуванням.
 */
export const options = {
  scenarios: {
    [SELECTED_SCENARIO]: allScenarios[SELECTED_SCENARIO] || allScenarios.smoke,
  },
  thresholds,
  noConnectionReuse: false,
  userAgent: 'ContractorAcceptanceGate-k6/1.0',
};
