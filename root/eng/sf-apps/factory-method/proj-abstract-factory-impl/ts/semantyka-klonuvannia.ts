class SqlCommand {
  constructor(public sql: string, public params: unknown[]) {}
  cloneShallow(): SqlCommand {                   // params — ТА САМА ланка
    return new SqlCommand(this.sql, this.params);
  }
  cloneDeep(): SqlCommand {                       // params — власна копія
    return new SqlCommand(this.sql, [...this.params]);
  }
}

const proto = new SqlCommand("INSERT INTO users(name) VALUES (?)", []);

const a = proto.cloneShallow();
const b = proto.cloneShallow();
a.params.push("Ann");
console.log(b.params);      // ["Ann"]  ← b теж має Ann: масив СПІЛЬНИЙ
console.log(proto.params);  // ["Ann"]  ← і сам взірець забруднено

const clean = new SqlCommand("INSERT INTO users(name) VALUES (?)", []);
const c = clean.cloneDeep();
const d = clean.cloneDeep();
c.params.push("Bob");
console.log(d.params);      // []  ← незалежні, як і має бути
