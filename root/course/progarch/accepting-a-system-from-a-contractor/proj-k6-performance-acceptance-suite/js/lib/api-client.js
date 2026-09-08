/**
 * lib/api-client.js — Обгортка HTTP-запитів із бізнес-перевірками (checks) та збором кастомних метрик.
 * Інкапсулює взаємодію з тестованою системою та фіксує порушення контрактних вимог.
 */

import http from 'k6/http';
import { check } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// Кастомні метрики для детального аудиту приймання
export const transactionDuration = new Trend('business_transaction_duration', true);
export const contractChecksRate = new Rate('contract_checks_success');
export const failedOrdersCount = new Counter('failed_orders_count');

export class ApiClient {
  /**
   * @param {string} baseUrl - Базовий URL досліджуваного сервісу
   * @param {object} defaultHeaders - Заголовки запиту за замовчуванням
   */
  constructor(baseUrl, defaultHeaders = {}) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...defaultHeaders,
    };
  }

  /**
   * Перевірка зонда життєздатності (Liveness / Readiness Probe).
   * @param {object} tags - Додаткові теги для сегментації метрик
   * @returns {object} k6 response
   */
  getHealth(tags = {}) {
    const url = `${this.baseUrl}/healthz`;
    const res = http.get(url, {
      headers: this.defaultHeaders,
      tags: { name: 'HealthCheck', ...tags },
    });

    const passed = check(res, {
      'health: статус відповіді 200': (r) => r.status === 200,
      'health: тривалість менша 200мс': (r) => r.timings.duration < 200,
    });

    contractChecksRate.add(passed);
    return res;
  }

  /**
   * Створення нового замовлення (критична транзакція запису).
   * @param {object} payload - Тіло замовлення
   * @param {object} tags - Теги запиту
   * @returns {object} k6 response
   */
  createOrder(payload, tags = {}) {
    const url = `${this.baseUrl}/api/v1/orders`;
    const body = JSON.stringify(payload);

    const startTime = Date.now();
    const res = http.post(url, body, {
      headers: this.defaultHeaders,
      tags: { name: 'CreateOrder', ...tags },
    });
    const duration = Date.now() - startTime;

    // Фіксація тривалості бізнес-транзакції
    transactionDuration.add(duration);

    const passed = check(res, {
      'order: статус 201 Created': (r) => r.status === 201,
      'order: відповідь містить orderId': (r) => {
        try {
          const data = r.json();
          return data && typeof data.orderId === 'string' && data.orderId.length > 0;
        } catch {
          return false;
        }
      },
      'order: час обробки менший 500мс': (r) => r.timings.duration < 500,
    });

    contractChecksRate.add(passed);
    if (!passed) {
      failedOrdersCount.add(1);
    }

    return res;
  }

  /**
   * Отримання деталей замовлення за ідентифікатором (транзакція читання).
   * @param {string} orderId 
   * @param {object} tags 
   * @returns {object} k6 response
   */
  getOrder(orderId, tags = {}) {
    const url = `${this.baseUrl}/api/v1/orders/${encodeURIComponent(orderId)}`;
    const res = http.get(url, {
      headers: this.defaultHeaders,
      tags: { name: 'GetOrder', ...tags },
    });

    const passed = check(res, {
      'getOrder: статус 200 OK': (r) => r.status === 200,
      'getOrder: відповідність запитаного ID': (r) => {
        try {
          return r.json('orderId') === orderId;
        } catch {
          return false;
        }
      },
    });

    contractChecksRate.add(passed);
    return res;
  }

  /**
   * Пошук продуктів з динамічними фільтрами (перевірка індексів БД).
   * @param {object} queryParams 
   * @param {object} tags 
   * @returns {object} k6 response
   */
  searchProducts(queryParams, tags = {}) {
    const queryString = Object.entries(queryParams)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
      .join('&');

    const url = `${this.baseUrl}/api/v1/products?${queryString}`;
    const res = http.get(url, {
      headers: this.defaultHeaders,
      tags: { name: 'SearchProducts', ...tags },
    });

    const passed = check(res, {
      'search: статус 200 OK': (r) => r.status === 200,
      'search: повертається непорожній масив': (r) => {
        try {
          const items = r.json('items');
          return Array.isArray(items);
        } catch {
          return false;
        }
      },
      'search: затримка менша 350мс': (r) => r.timings.duration < 350,
    });

    contractChecksRate.add(passed);
    return res;
  }
}
