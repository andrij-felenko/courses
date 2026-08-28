export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const cacheKey = new Request(url.toString(), request);
    const cache = caches.default;

    // 1. Спроба вибірки з локального крайового кешу
    let response = await cache.match(cacheKey);

    if (!response) {
      // 2. Cache Miss: запит на Origin
      response = await fetch(request);

      // 3. Модифікація заголовків перед збереженням
      const headers = new Headers(response.headers);
      headers.set("Cache-Control", "public, max-age=86400, stale-while-revalidate=60");
      headers.set("Surrogate-Key", "catalog-products brand-sony");

      response = new Response(response.body, { ...response, headers });

      // 4. Асинхронний запис у кеш без затримки клієнтської відповіді
      ctx.waitUntil(cache.put(cacheKey, response.clone()));
    }

    return response;
  }
};
