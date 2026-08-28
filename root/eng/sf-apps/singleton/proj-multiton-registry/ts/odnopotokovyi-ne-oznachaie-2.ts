class PoolRegistry {
  private pools = new Map<string, Pool>();
  private inflight = new Map<string, Promise<Pool>>();

  get(key: string): Promise<Pool> {
    const ready = this.pools.get(key);
    if (ready) return Promise.resolve(ready);      // уже готовий

    // ключова хитрість: кешуємо саму ОБІЦЯНКУ побудови, а не лише готовий пул.
    // Другий виклик під час будівництва дістане ТУ САМУ обіцянку й дочекається її,
    // а не почне будувати другий пул.
    let building = this.inflight.get(key);
    if (!building) {
      building = createPool(key).then(pool => {
        this.pools.set(key, pool);
        this.inflight.delete(key);
        return pool;
      });
      this.inflight.set(key, building);
    }
    return building;
  }
}
