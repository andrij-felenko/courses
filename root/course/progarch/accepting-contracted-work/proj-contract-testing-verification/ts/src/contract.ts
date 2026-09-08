import * as fs from "node:fs";
import * as path from "node:path";

/** Підтримувані HTTP-методи для контрактних взаємодій */
export type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

/** Специфікація очікуваного HTTP-запиту в контракті */
export interface HttpRequestDefinition {
  method: HttpMethod;
  path: string;
  headers?: Record<string, string>;
  body?: unknown;
}

/** Специфікація очікуваної HTTP-відповіді в контракті */
export interface HttpResponseDefinition {
  status: number;
  headers?: Record<string, string>;
  body?: unknown;
}

/** Одиниця взаємодії (Interaction) між споживачем і провайдером */
export interface Interaction {
  description: string;
  providerState: string;
  request: HttpRequestDefinition;
  response: HttpResponseDefinition;
}

/** Структура артефакту JSON-контракту взаємодії */
export interface Contract {
  consumer: { name: string };
  provider: { name: string };
  interactions: Interaction[];
  metadata: {
    createdAt: string;
    specificationVersion: string;
  };
}

/** Доменна модель акту/результату робіт підрядника */
export interface Deliverable {
  id: string;
  title: string;
  contractor: string;
  status: "SUBMITTED" | "ACCEPTED" | "REJECTED";
  artifactsCount: number;
}

/** Тіло запиту на фінальне приймання робіт */
export interface AcceptDeliverableRequest {
  acceptedBy: string;
  comment: string;
}

/** Відповідь на успішне приймання */
export interface AcceptDeliverableResponse {
  id: string;
  status: "ACCEPTED";
  acceptedAt: string;
}

/** Збереження контракту у файл JSON на диску */
export function saveContract(contract: Contract, filePath: string): void {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(filePath, JSON.stringify(contract, null, 2), "utf8");
}

/** Завантаження контракту з файлу JSON */
export function loadContract(filePath: string): Contract {
  const raw = fs.readFileSync(filePath, "utf8");
  return JSON.parse(raw) as Contract;
}

/**
 * Рекурсивне зіставлення очікуваного та фактичного корисного навантаження (Payload matching).
 * Перевіряє, що фактичні дані містять усі очікувані контрактом поля та типи.
 */
export function matchPayload(
  expected: unknown,
  actual: unknown,
  currentPath = "root"
): { matches: boolean; differences: string[] } {
  const differences: string[] = [];

  if (expected === actual) {
    return { matches: true, differences: [] };
  }

  if (expected === null || expected === undefined || actual === null || actual === undefined) {
    if (expected !== actual) {
      differences.push(`Помилка у ${currentPath}: очікувалося ${JSON.stringify(expected)}, отримано ${JSON.stringify(actual)}`);
    }
    return { matches: differences.length === 0, differences };
  }

  if (typeof expected !== typeof actual) {
    differences.push(`Невідповідність типу у ${currentPath}: очікувався ${typeof expected}, отримано ${typeof actual}`);
    return { matches: false, differences };
  }

  if (Array.isArray(expected)) {
    if (!Array.isArray(actual)) {
      differences.push(`Помилка у ${currentPath}: очікувався масив`);
      return { matches: false, differences };
    }
    if (expected.length !== actual.length) {
      differences.push(`Помилка довжини масиву у ${currentPath}: очікувалося ${expected.length}, отримано ${actual.length}`);
    }
    const maxLen = Math.min(expected.length, actual.length);
    for (let i = 0; i < maxLen; i++) {
      const sub = matchPayload(expected[i], actual[i], `${currentPath}[${i}]`);
      differences.push(...sub.differences);
    }
    return { matches: differences.length === 0, differences };
  }

  if (typeof expected === "object") {
    const expObj = expected as Record<string, unknown>;
    const actObj = actual as Record<string, unknown>;

    for (const key of Object.keys(expObj)) {
      if (!(key in actObj)) {
        differences.push(`Відсутнє обов'язкове поле у ${currentPath}.${key}`);
      } else {
        const sub = matchPayload(expObj[key], actObj[key], `${currentPath}.${key}`);
        differences.push(...sub.differences);
      }
    }
    return { matches: differences.length === 0, differences };
  }

  if (expected !== actual) {
    differences.push(`Значення не збігається у ${currentPath}: очікувалося ${expected}, отримано ${actual}`);
  }

  return { matches: differences.length === 0, differences };
}
