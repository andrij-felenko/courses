/**
 * main.js — Головна точка входу в тестовий пакет k6 для приймання системи від підрядника.
 * Виконує навантажувальний сценарій та формує підсумковий машинний звіт через handleSummary.
 */

import { sleep } from 'k6';
import { options, TARGET_URL, SELECTED_SCENARIO } from './config/options.js';
import { ApiClient } from './lib/api-client.js';
import { generateOrderPayload, generateSearchQuery, randomInt } from './data/payloads.js';
import { SummaryReporter } from './reporters/summary-reporter.js';

// Експорт конфігурації options для k6 runtime
export { options };

// Ініціалізація клієнта API для тестованого екземпляра
const client = new ApiClient(TARGET_URL);

/**
 * Ініціалізація тестового середовища (виконується один раз перед тестами).
 */
export function setup() {
  // Перевірка доступності тестованого стенду перед початком навантаження
  const healthRes = client.getHealth({ stage: 'setup' });
  if (healthRes.status !== 200) {
    throw new Error(
      `Стенд підрядника недоступний за адресою ${TARGET_URL}. Приймальне тестування зупинено.`
    );
  }
  return { startTime: Date.now(), scenario: SELECTED_SCENARIO };
}

/**
 * Головний цикл віртуального користувача (VU).
 * Моделює типовий бізнес-сценарій взаємодії клієнта із системою.
 */
export default function (data) {
  // 1. Зондування готовності (Health Probe)
  client.getHealth();

  // 2. Пошук каталогу продуктів із динамічними фільтрами
  const searchPayload = generateSearchQuery();
  const searchRes = client.searchProducts(searchPayload);

  // 3. Створення бізнес-замовлення з унікалізованим тілом
  const vuId = typeof __VU !== 'undefined' ? __VU : 1;
  const iter = typeof __ITER !== 'undefined' ? __ITER : 0;
  const orderPayload = generateOrderPayload(vuId, iter);
  const orderRes = client.createOrder(orderPayload);

  // 4. Якщо замовлення створено успішно — перевіряємо його читанням
  if (orderRes.status === 201) {
    try {
      const orderBody = orderRes.json();
      if (orderBody && orderBody.orderId) {
        client.getOrder(orderBody.orderId);
      }
    } catch {
      // Помилка парсингу буде зафіксована у Checks клієнта
    }
  }

  // 5. Пауза мислення користувача (Pacing / Think Time) для уникнення надмірного спаму
  sleep(randomInt(1, 2));
}

/**
 * Генерація кастомного звіту після завершення всіх сценаріїв k6.
 * Створює машинозчитуваний JSON-артефакт для блокуючого шлюзу CI/CD.
 * @param {object} data - Зведені результати тестування від k6
 * @returns {object} Мапа файлів артефактів для k6
 */
export function handleSummary(data) {
  const reporter = new SummaryReporter();
  const report = reporter.generate(data, 'Contractor-Delivery-Acceptance');
  const consoleOutput = reporter.formatConsole(report);

  return {
    // Людиночитаний вивід у консоль CI/CD
    stdout: consoleOutput,
    // Машинозчитуваний звіт для валідації якості у конвеєрі
    'acceptance-summary.json': JSON.stringify(report, null, 2),
  };
}
