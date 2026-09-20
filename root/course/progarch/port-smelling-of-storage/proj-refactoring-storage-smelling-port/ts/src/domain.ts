/**
 * Доменний шар: чисті бізнес-сутності, об'єкти-значення та правила комплектації.
 * Цей модуль повністю позбавлений будь-яких залежностей від баз даних, ORM або фреймворків.
 */

export class DomainError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'DomainError';
  }
}

export class InvalidOrderStateError extends DomainError {
  constructor(orderId: string, currentStatus: string, action: string) {
    super(
      `Неможливо виконати дію "${action}" для замовлення ${orderId}: поточний статус "${currentStatus}".`
    );
    this.name = 'InvalidOrderStateError';
  }
}

/**
 * Об'єкт-значення (Value Object) ідентифікатора замовлення.
 * Забезпечує самовалідацію формату UUID та унеможливлює проникнення
 * числових auto-increment ID бази даних у доменне ядро.
 */
export class OrderId {
  private static readonly UUID_REGEX =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

  private readonly value: string;

  private constructor(value: string) {
    const trimmed = value.trim();
    if (!OrderId.UUID_REGEX.test(trimmed)) {
      throw new DomainError(
        `Некоректний формат OrderId: "${value}". Очікується стандартний UUID v4.`
      );
    }
    this.value = trimmed.toLowerCase();
  }

  public static of(value: string): OrderId {
    return new OrderId(value);
  }

  public static generate(): OrderId {
    // Детермінована автономна генерація UUID v4 без зовнішніх залежностей
    const hexDigits = '0123456789abcdef';
    let s = '';
    for (let i = 0; i < 36; i++) {
      if (i === 8 || i === 13 || i === 18 || i === 23) {
        s += '-';
      } else if (i === 14) {
        s += '4';
      } else if (i === 19) {
        s += hexDigits[((Math.random() * 4) | 0) + 8];
      } else {
        s += hexDigits[(Math.random() * 16) | 0];
      }
    }
    return new OrderId(s);
  }

  public toString(): string {
    return this.value;
  }

  public equals(other: OrderId | null | undefined): boolean {
    if (!other) return false;
    return this.value === other.value;
  }
}

export type OrderStatus = 'PENDING' | 'IN_FULFILLMENT' | 'FULFILLED' | 'CANCELLED';

export interface OrderItem {
  readonly sku: string;
  readonly name: string;
  readonly quantity: number;
  readonly unitPriceCents: number;
}

/**
 * Незмінний знімок стану замовлення для безпечного експорту та персистенції.
 */
export interface OrderSnapshot {
  readonly id: string;
  readonly status: OrderStatus;
  readonly items: readonly OrderItem[];
  readonly totalAmountCents: number;
  readonly createdAt: Date;
  readonly fulfilledAt: Date | null;
}

/**
 * Доменна сутність замовлення.
 * Керує бізнес-статусом комплектації, інкапсулює стан без розкриття сетерів
 * і гарантує збереження інваріантів переходу станів.
 */
export class Order {
  private readonly id: OrderId;
  private status: OrderStatus;
  private readonly items: readonly OrderItem[];
  private readonly totalAmountCents: number;
  private readonly createdAt: Date;
  private fulfilledAt: Date | null;

  private constructor(
    id: OrderId,
    status: OrderStatus,
    items: readonly OrderItem[],
    totalAmountCents: number,
    createdAt: Date,
    fulfilledAt: Date | null
  ) {
    this.id = id;
    this.status = status;
    this.items = [...items];
    this.totalAmountCents = totalAmountCents;
    this.createdAt = createdAt;
    this.fulfilledAt = fulfilledAt;
  }

  public static create(id: OrderId, items: readonly OrderItem[]): Order {
    if (items.length === 0) {
      throw new DomainError('Замовлення повинно містити щонайменше один товар.');
    }
    for (const item of items) {
      if (item.quantity <= 0) {
        throw new DomainError(`Кількість товару ${item.sku} має бути більшою за нуль.`);
      }
      if (item.unitPriceCents < 0) {
        throw new DomainError(`Ціна товару ${item.sku} не може бути від'ємною.`);
      }
    }

    const total = items.reduce((sum, item) => sum + item.unitPriceCents * item.quantity, 0);
    return new Order(id, 'PENDING', items, total, new Date(), null);
  }

  /**
   * Відновлення сутності зі знімка стану (використовується адаптерами збереження).
   */
  public static reconstitute(snapshot: OrderSnapshot): Order {
    return new Order(
      OrderId.of(snapshot.id),
      snapshot.status,
      snapshot.items,
      snapshot.totalAmountCents,
      new Date(snapshot.createdAt),
      snapshot.fulfilledAt ? new Date(snapshot.fulfilledAt) : null
    );
  }

  public getId(): OrderId {
    return this.id;
  }

  public getStatus(): OrderStatus {
    return this.status;
  }

  public isPending(): boolean {
    return this.status === 'PENDING';
  }

  /**
   * Переведення замовлення в процес комплектації.
   */
  public startFulfillment(): void {
    if (this.status !== 'PENDING') {
      throw new InvalidOrderStateError(this.id.toString(), this.status, 'startFulfillment');
    }
    this.status = 'IN_FULFILLMENT';
  }

  /**
   * Фіксація успішної комплектації замовлення.
   */
  public fulfill(completionDate: Date = new Date()): void {
    if (this.status !== 'PENDING' && this.status !== 'IN_FULFILLMENT') {
      throw new InvalidOrderStateError(this.id.toString(), this.status, 'fulfill');
    }
    this.status = 'FULFILLED';
    this.fulfilledAt = completionDate;
  }

  /**
   * Скасування замовлення.
   */
  public cancel(): void {
    if (this.status === 'FULFILLED') {
      throw new DomainError(
        `Неможливо скасувати замовлення ${this.id.toString()}, оскільки воно вже укомплектоване.`
      );
    }
    this.status = 'CANCELLED';
  }

  /**
   * Створення незмінного знімка поточного стану без надання прямих мутаторів.
   */
  public toSnapshot(): OrderSnapshot {
    return {
      id: this.id.toString(),
      status: this.status,
      items: this.items.map(item => ({ ...item })),
      totalAmountCents: this.totalAmountCents,
      createdAt: new Date(this.createdAt),
      fulfilledAt: this.fulfilledAt ? new Date(this.fulfilledAt) : null,
    };
  }
}
