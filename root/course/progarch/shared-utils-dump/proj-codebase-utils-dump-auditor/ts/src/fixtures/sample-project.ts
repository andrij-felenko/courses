import * as ts from 'typescript';

/**
 * Синтетична кодова база, що демонструє антипатерн «utils як смітник»
 * та типові порушення модульної архітектури.
 *
 * Файлова структура віртуального проєкту:
 * /virtual/src/
 *   ├── domain/
 *   │   └── order.ts               (Доменні сутності та типи)
 *   ├── utils/
 *   │   └── shared-utils.ts        (Каталог-звалище, де зібрані несумісні речі)
 *   ├── orders/
 *   │   └── checkout-service.ts    (Споживач розрахунку знижки замовлення)
 *   ├── billing/
 *   │   └── invoice-generator.ts   (Єдиний споживач форматування валюти)
 *   ├── catalog/
 *   │   └── product-service.ts     (Споживач універсального слага)
 *   ├── blog/
 *   │   └── article-service.ts     (Споживач універсального слага)
 *   └── users/
 *       └── profile-service.ts     (Споживач універсального слага)
 */
export const SAMPLE_PROJECT_FILES: Record<string, string> = {
  // 1. Доменна модель: чисті сутності предметної області
  '/virtual/src/domain/order.ts': `
export interface Order {
  id: string;
  customerEmail: string;
  totalAmount: number;
  itemCount: number;
  createdAt: Date;
}

export type CustomerTier = 'STANDARD' | 'PREMIUM' | 'VIP';
`,

  // 2. Звалище спільних утиліт із 4 типовими архітектурними категоріями
  '/virtual/src/utils/shared-utils.ts': `
import { Order, CustomerTier } from '../domain/order';

/**
 * [АРХІТЕКТУРНИЙ ДЕФЕКТ: Витік предметної області / Domain Repatriation]
 * Сигнатура функції приймає доменні типи Order та CustomerTier.
 * Пряме порушення меж контекстів: бізнес-правило нарахування знижки
 * опинилося в доменно-нейтральному каталозі utils.
 */
export function calculateOrderDiscount(order: Order, tier: CustomerTier): number {
  if (tier === 'VIP') {
    return order.totalAmount * 0.15;
  }
  if (tier === 'PREMIUM') {
    return order.totalAmount * 0.08;
  }
  return 0;
}

/**
 * [АРХІТЕКТУРНИЙ ДЕФЕКТ: Кандидат на інлайнінг / Порушення CRP]
 * Допоміжна функція форматування валюти для рахунка-фактури.
 * Потрібна ТІЛЬКИ модулю білінгу (billing), але лежить у спільних utils.
 * Порушує Common Reuse Principle (CRP): змушує всіх споживачів utils залежати від формату білінгу.
 */
export function formatInvoiceCurrency(amount: number, currencyCode: string): string {
  return amount.toFixed(2) + ' ' + currencyCode.toUpperCase();
}

/**
 * [АРХІТЕКТУРНИЙ ДЕФЕКТ: Мертвий код / Dead Code]
 * Залишок застарілої системи v1, експортований утилітою.
 * Жодного разу не викликається в кодовій базі.
 */
export function unserializeLegacySession(raw: string): Record<string, unknown> {
  return JSON.parse(raw);
}

/**
 * [ЛЕГІТИМНА СПІЛЬНА УТИЛІТА: Відповідає принципам CRP та REP]
 * Універсальне перетворення рядка на URL-slug.
 * Доменно-нейтральна (оперує примітивом string), не має бізнес-залежностей,
 * активно використовується у трьох незалежних підсистемах (catalog, blog, users).
 */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\\w\\s-]/g, '')
    .replace(/[\\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
`,

  // 3. Модуль оформлення замовлень (споживач доменної функції з utils)
  '/virtual/src/orders/checkout-service.ts': `
import { Order, CustomerTier } from '../domain/order';
import { calculateOrderDiscount } from '../utils/shared-utils';

export class CheckoutService {
  public processCheckout(order: Order, tier: CustomerTier): number {
    const discount = calculateOrderDiscount(order, tier);
    return order.totalAmount - discount;
  }
}
`,

  // 4. Модуль білінгу (єдиний споживач formatInvoiceCurrency)
  '/virtual/src/billing/invoice-generator.ts': `
import { formatInvoiceCurrency } from '../utils/shared-utils';

export class InvoiceGenerator {
  public generateLine(amount: number, currency: string): string {
    return 'Сума до сплати: ' + formatInvoiceCurrency(amount, currency);
  }
}
`,

  // 5. Каталог товарів (споживач 1 для slugify)
  '/virtual/src/catalog/product-service.ts': `
import { slugify } from '../utils/shared-utils';

export class ProductService {
  public createProductUrl(productTitle: string): string {
    return '/products/' + slugify(productTitle);
  }
}
`,

  // 6. Блог та публікації (споживач 2 для slugify)
  '/virtual/src/blog/article-service.ts': `
import { slugify } from '../utils/shared-utils';

export class ArticleService {
  public buildArticleSlug(heading: string): string {
    return '/blog/' + slugify(heading);
  }
}
`,

  // 7. Профілі користувачів (споживач 3 для slugify)
  '/virtual/src/users/profile-service.ts': `
import { slugify } from '../utils/shared-utils';

export class ProfileService {
  public generateHandle(username: string): string {
    return '@' + slugify(username);
  }
}
`,

  // 8. Мінімальний віртуальний lib.d.ts для роботи TypeScript Compiler API без файлової системи
  '/virtual/lib.d.ts': `
interface Boolean {}
interface Function {}
interface Number {
  toFixed(digits?: number): string;
}
interface IArguments {}
interface RegExp {}
interface String {
  toLowerCase(): string;
  trim(): string;
  replace(searchValue: string | RegExp, replaceValue: string): string;
  toUpperCase(): string;
}
interface Array<T> {
  length: number;
  [n: number]: T;
}
interface ReadonlyArray<T> {
  readonly length: number;
  readonly [n: number]: T;
}
interface Object {}
interface Date {
  getTime(): number;
}
declare var JSON: {
  parse(text: string): any;
};
type Record<K extends keyof any, T> = { [P in K]: T; };
`,
};

/**
 * Ініціалізує повністю автономну віртуальну ts.Program у пам'яті
 * для демонстрації аудитора без залежності від фізичного диска.
 */
export function createSampleProjectProgram(): {
  program: ts.Program;
  utilsFiles: string[];
} {
  const files = SAMPLE_PROJECT_FILES;
  const rootFileNames = Object.keys(files).filter((p) => p !== '/virtual/lib.d.ts');

  const options: ts.CompilerOptions = {
    target: ts.ScriptTarget.ES2022,
    module: ts.ModuleKind.CommonJS,
    moduleResolution: ts.ModuleResolutionKind.NodeJs,
    strict: true,
    noLib: true,
  };

  // Кастомний віртуальний CompilerHost для резолвінгу файлів у пам'яті
  const host: ts.CompilerHost = {
    getSourceFile: (fileName, languageVersion) => {
      const normalized = fileName.replace(/\\/g, '/');
      const content = files[normalized];
      if (content !== undefined) {
        return ts.createSourceFile(normalized, content, languageVersion, true);
      }
      return undefined;
    },
    getDefaultLibFileName: () => '/virtual/lib.d.ts',
    writeFile: () => {},
    getCurrentDirectory: () => '/virtual',
    getDirectories: () => [],
    getCanonicalFileName: (fileName) => fileName.replace(/\\/g, '/'),
    useCaseSensitiveFileNames: () => true,
    getNewLine: () => '\n',
    fileExists: (fileName) => {
      const normalized = fileName.replace(/\\/g, '/');
      return (
        normalized in files ||
        `${normalized}.ts` in files ||
        `${normalized}/index.ts` in files
      );
    },
    readFile: (fileName) => {
      const normalized = fileName.replace(/\\/g, '/');
      return files[normalized] ?? files[`${normalized}.ts`];
    },
    resolveModuleNames: (moduleNames, containingFile) => {
      return moduleNames.map((moduleName) => {
        let resolvedPath = '';
        if (moduleName.startsWith('.')) {
          const containingDir = containingFile.substring(
            0,
            containingFile.lastIndexOf('/')
          );
          const parts = `${containingDir}/${moduleName}`.split('/');
          const resolvedParts: string[] = [];
          for (const p of parts) {
            if (p === '.' || p === '') continue;
            if (p === '..') resolvedParts.pop();
            else resolvedParts.push(p);
          }
          resolvedPath = '/' + resolvedParts.join('/');
        } else {
          resolvedPath = `/virtual/${moduleName}`;
        }

        const candidate = resolvedPath.endsWith('.ts')
          ? resolvedPath
          : `${resolvedPath}.ts`;

        if (candidate in files) {
          return {
            resolvedFileName: candidate,
            isExternalLibraryImport: false,
            extension: ts.Extension.Ts,
          };
        }
        return undefined;
      });
    },
  };

  const program = ts.createProgram(rootFileNames, options, host);

  return {
    program,
    utilsFiles: ['/virtual/src/utils/shared-utils.ts'],
  };
}
