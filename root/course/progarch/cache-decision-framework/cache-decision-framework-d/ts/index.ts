async function getDeviceProfile(id: string): Promise<Profile> {
  const key = `device:${id}`;
  const hit = await cache.get(key);
  if (hit) return JSON.parse(hit);              // влучили — швидко, та, можливо, несвіже

  const fresh = await db.loadProfile(id);        // промах — ідемо до джерела
  await cache.set(key, JSON.stringify(fresh), { ttlSeconds: 60 });  // TTL = бюджет несвіжості
  return fresh;
  // пастка: якщо ключ протух і тисяча читань промахнулись РАЗОМ,
  // усі тисяча ринуть у джерело одночасно — «гримуча отара» (ворота 5)
}

async function renameDevice(id: string, name: string): Promise<void> {
  await db.rename(id, name);
  await cache.del(`device:${id}`);               // інвалідація на запис: копію треба скинути
}
