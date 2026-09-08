/**
 * data/payloads.js — Генератор параметризованих тестових даних для навантажувального аудиту.
 * Запобігає штучному кешуванню на стороні веб-сервера чи СУБД завдяки унікалізації ключів.
 */

/**
 * Генерація випадкового рядка заданої довжини.
 * @param {number} length 
 * @returns {string}
 */
export function randomString(length = 8) {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * Генерація випадкового цілого числа у діапазоні [min, max].
 * @param {number} min 
 * @param {number} max 
 * @returns {number}
 */
export function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Формує унікальне тіло запиту на створення бізнес-замовлення.
 * @param {number} vuId - ID віртуального користувача
 * @param {number} iteration - Номер поточної ітерації
 * @returns {object}
 */
export function generateOrderPayload(vuId = 1, iteration = 0) {
  const categories = ['electronics', 'books', 'hardware', 'office', 'cloud-services'];
  const category = categories[randomInt(0, categories.length - 1)];
  const itemCount = randomInt(1, 5);

  const items = [];
  for (let i = 0; i < itemCount; i++) {
    items.push({
      sku: `SKU-${category.toUpperCase()}-${randomInt(100, 999)}`,
      quantity: randomInt(1, 4),
      unitPrice: Number((randomInt(50, 500) + Math.random()).toFixed(2)),
    });
  }

  return {
    clientRequestId: `req-${vuId}-${iteration}-${Date.now()}-${randomString(6)}`,
    customerId: `cust-${randomInt(1000, 9999)}`,
    category,
    items,
    metadata: {
      generatedAt: new Date().toISOString(),
      syntheticAudit: true,
      nonce: randomString(12),
    },
  };
}

/**
 * Формує випадковий пошуковий запит для перевірки читального навантаження.
 * @returns {object}
 */
export function generateSearchQuery() {
  const keywords = ['payment', 'transfer', 'invoice', 'gateway', 'settlement', 'balance'];
  const keyword = keywords[randomInt(0, keywords.length - 1)];

  return {
    q: `${keyword}-${randomString(4)}`,
    limit: randomInt(5, 20),
    offset: randomInt(0, 5) * 10,
    timestamp: Date.now(),
  };
}
