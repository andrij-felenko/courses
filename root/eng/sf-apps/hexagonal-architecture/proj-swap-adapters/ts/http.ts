// adapters/http.ts ── ДРАЙВЕР-АДАПТЕР. Залежить від ПОРТУ, не від сервісу.
import { ОформленняЗамовлення } from "../order/core";

export class ЗамовленняHttp {
  constructor(private застосунок: ОформленняЗамовлення) {} // ← порт, не клас

  async post(req: Request, res: Response) {
    try {
      const з = await this.застосунок.оформити(req.body.пошта, req.body.позиції);
      res.status(201).json({ id: з.id, сума: з.сума() });   // домен → HTTP
    } catch (e) {
      res.status(400).json({ помилка: (e as Error).message });
    }
  }
}
