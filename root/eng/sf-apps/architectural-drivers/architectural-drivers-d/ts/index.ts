const cache = new Map<string, User>();

function getUser(id: string): User {
  const hit = cache.get(id);        // тактика: кеш заради швидкодії
  if (hit) return hit;
  const user = db.queryUser(id);    // дорогий похід у базу
  cache.set(id, user);
  return user;
}

function renameUser(id: string, name: string): void {
  db.updateUser(id, name);
  // Прихована ціна: без інвалідації кеш віддаватиме старе ім'я.
  cache.delete(id);                 // борг, який породив кеш
}
