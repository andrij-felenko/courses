class MemoryStore implements Store {                 // у проді — Redis, API ідентичний
  private m = new Map<string, string>();
  async get(k: string) { return this.m.get(k) ?? null; }
  async set(k: string, v: string) { this.m.set(k, v); }
  async del(k: string) { this.m.delete(k); }
}

const alice: Principal = { sub: "u-42", home: "home-7", scopes: ["door:unlock"] };
const seamA = new ServerStoreSeam(new MemoryStore());

const sid = await seamA.login(alice);
console.log(await seamA.validate(sid)); // → { sub: 'u-42', … }  ЖИВА
await seamA.revoke(sid);                //   ← «викинули телефон»: видалили запис
console.log(await seamA.validate(sid)); // → null                МЕРТВА В ТУ Ж МИТЬ
