import { DatabaseSync } from "node:sqlite";

export class StaleObject extends Error {}

type Row = Record<string, unknown>;
const q = (s: string) => `"${s.replace(/"/g, '""')}"`;

export class Model {
  static table = "";
  static pk = "id";
  static version: string | null = null;
  static db: DatabaseSync;
  static _columns?: string[];

  // ── схема: клас питає базу, які в нього поля ──
  static columns(): string[] {
    if (!Object.hasOwn(this, "_columns")) {         // кеш саме цього класу
      const info = this.db
        .prepare(`PRAGMA table_info(${q(this.table)})`)
        .all() as { name: string }[];
      if (info.length === 0) throw new Error(`таблиці ${q(this.table)} немає`);
      this._columns = info.map((r) => r.name);
    }
    return this._columns!;
  }

  _data: Row = {};
  _dirty = new Set<string>();

  constructor(fields: Row = {}) {
    const cls = new.target as typeof Model;
    for (const c of cls.columns()) this._data[c] = null;
    const self = new Proxy(this, HANDLER);
    Object.assign(self, fields);
    return self;                                    // назовні віддаємо посередника
  }

  get changes(): Row {
    const out: Row = {};
    for (const c of [...this._dirty].sort()) out[c] = this._data[c];
    return out;
  }

  // ── читання ──
  static fromRow<T extends typeof Model>(this: T, row: Row): InstanceType<T> {
    const obj = Object.create(this.prototype) as Model;
    obj._data = { ...row };
    obj._dirty = new Set();                         // щойно з бази → чистий
    return new Proxy(obj, HANDLER) as InstanceType<T>;
  }

  static find<T extends typeof Model>(this: T, key: unknown): InstanceType<T> | null {
    const names = this.columns().map(q).join(", ");
    const row = this.db
      .prepare(`SELECT ${names} FROM ${q(this.table)} WHERE ${q(this.pk)} = ?`)
      .get(key as never) as Row | undefined;
    return row ? this.fromRow(row) : null;
  }

  static where<T extends typeof Model>(this: T, cond: Row = {}): InstanceType<T>[] {
    const keys = Object.keys(cond);
    for (const k of keys)
      if (!this.columns().includes(k))              // у SQL іде лише те, що дала схема
        throw new Error(`колонки ${q(k)} в ${this.table} немає`);
    const names = this.columns().map(q).join(", ");
    let sql = `SELECT ${names} FROM ${q(this.table)}`;
    if (keys.length) sql += " WHERE " + keys.map((k) => `${q(k)} = ?`).join(" AND ");
    const rows = this.db.prepare(sql).all(...(Object.values(cond) as never[])) as Row[];
    return rows.map((r) => this.fromRow(r));
  }

  // ── запис ──
  save(): number {
    const cls = this.constructor as typeof Model;
    return this._data[cls.pk] === null || this._data[cls.pk] === undefined
      ? this.insert()
      : this.update();
  }

  private insert(): number {
    const cls = this.constructor as typeof Model;
    if (cls.version) {
      this._data[cls.version] = 0;
      this._dirty.add(cls.version);
    }
    const cols = cls.columns().filter((c) => this._dirty.has(c));
    let info;
    if (cols.length) {
      const names = cols.map(q).join(", ");
      const marks = cols.map(() => "?").join(", ");
      info = cls.db
        .prepare(`INSERT INTO ${q(cls.table)} (${names}) VALUES (${marks})`)
        .run(...(cols.map((c) => this._data[c]) as never[]));
    } else {
      info = cls.db.prepare(`INSERT INTO ${q(cls.table)} DEFAULT VALUES`).run();
    }
    this._data[cls.pk] = Number(info.lastInsertRowid);
    this._dirty.clear();
    return 1;
  }

  private update(): number {
    const cls = this.constructor as typeof Model;
    const cols = cls
      .columns()
      .filter((c) => this._dirty.has(c) && c !== cls.pk && c !== cls.version);
    if (!cols.length) return 0;                     // нічого не змінилося — жодного запиту

    const sets = cols.map((c) => `${q(c)} = ?`);
    const args: unknown[] = cols.map((c) => this._data[c]);
    let where = `${q(cls.pk)} = ?`;
    const wargs: unknown[] = [this._data[cls.pk]];

    let seen = 0;
    if (cls.version) {
      seen = Number(this._data[cls.version] ?? 0);
      sets.push(`${q(cls.version)} = ?`);
      args.push(seen + 1);
      where += ` AND ${q(cls.version)} = ?`;        // рядок мусить бути тим, що ми читали
      wargs.push(seen);
    }
    const info = cls.db
      .prepare(`UPDATE ${q(cls.table)} SET ${sets.join(", ")} WHERE ${where}`)
      .run(...([...args, ...wargs] as never[]));
    if (Number(info.changes) !== 1)                 // 0 рядків → версія вже не наша
      throw new StaleObject(`${cls.name} ${this._data[cls.pk]}: рядок змінили`);
    if (cls.version) this._data[cls.version] = seen + 1;
    this._dirty.clear();
    return 1;
  }

  delete(): number {
    const cls = this.constructor as typeof Model;
    const key = this._data[cls.pk];
    if (key === null || key === undefined) return 0;
    const info = cls.db
      .prepare(`DELETE FROM ${q(cls.table)} WHERE ${q(cls.pk)} = ?`)
      .run(key as never);
    this._data[cls.pk] = null;                      // ключа немає → рядка немає
    this._dirty = new Set(
      cls.columns().filter((c) => c !== cls.pk && this._data[c] !== null),
    );
    return Number(info.changes);
  }
}

const HANDLER: ProxyHandler<Model> = {
  get(t, k, recv) {
    // hasOwn, а не `in`: інакше "constructor" знайдеться в прототипі _data
    if (typeof k === "string" && Object.hasOwn(t._data, k)) return t._data[k];
    return Reflect.get(t, k, recv);
  },
  set(t, k, v) {
    const cls = t.constructor as typeof Model;
    if (typeof k === "string" && cls.columns().includes(k)) {
      if (t._data[k] !== v) t._dirty.add(k);        // те саме значення не бруднить
      t._data[k] = v;
      return true;
    }
    return Reflect.set(t, k, v);
  },
};
