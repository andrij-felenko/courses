// Аналог трирівневого кешу на TypeScript з використанням Singleflight
async getHomeState(
  homeId: string,
  originDBFetch: (id: string) => Promise<HomeState>
): Promise<HomeState> {
  const cacheKey = `dh:home:${homeId}`;

  // 1. L1 Process Memory Check
  if (this.l1Memory.has(cacheKey)) {
    return this.l1Memory.get(cacheKey)!;
  }

  // 2. L2 Redis Check
  const redisVal = await this.redisClient.get(cacheKey);
  if (redisVal) {
    const parsed = JSON.parse(redisVal) as HomeState;
    this.l1Memory.set(cacheKey, parsed);
    return parsed;
  }

  // 3. Singleflight Coalescing for Origin DB Fetch
  return this.singleflight.doCall(cacheKey, async () => {
    const freshState = await originDBFetch(homeId);
    await this.redisClient.set(cacheKey, JSON.stringify(freshState), "EX", 300);
    this.l1Memory.set(cacheKey, freshState);
    return freshState;
  });
}
