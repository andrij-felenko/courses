type Pk = number | string;
type Row = Record<string, unknown>;

type EntityClass = (new (...a: never[]) => Entity) & {
  readonly table: string;
  readonly columns: readonly string[];
  fromRow(row: Row): Entity;
};

abstract class Entity {
  readonly pk: Pk;
  session: Session | null = null;   // хто веде цей об'єкт; null — відчеплений

  constructor(pk: Pk) {
    this.pk = pk;
  }
}

class Order extends Entity {
  static readonly table = "orders";
  static readonly columns = ["status", "discount"] as const;

  status: string;
  discount: number;

  constructor(pk: Pk, status: string, discount: number) {
    super(pk);
    this.status = status;
    this.discount = discount;
  }

  static fromRow(row: Row): Order {
    return new Order(row.id as Pk, row.status as string, row.discount as number);
  }
}

// Пастка set спрацьовує В МИТЬ присвоєння. Конструктор її обходить сам собою:
// там ще немає ні проксі, ні сесії — складання з рядка бруду не робить.
function track<T extends Entity>(target: T, session: Session): T {
  const columns = (target.constructor as EntityClass).columns;
  const proxy: T = new Proxy(target, {
    set(t, prop, value) {
      const old = Reflect.get(t, prop);
      const ok = Reflect.set(t, prop, value);
      if (ok && old !== value && typeof prop === "string" && columns.includes(prop)) {
        session.markDirty(proxy, prop);   // саме proxy, а не t — див. пастки
      }
      return ok;
    },
  });
  return proxy;
}
