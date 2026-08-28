// ВХІД: перевірили пароль → знищили те, що приїхало → видали свіжий номер
async function login(req, res, username: string, password: string) {
  const user = await verifyPassword(username, password);   // автентифікація
  if (!user) return res.status(401).end();

  const incoming = parseCookie(req.headers.cookie).sid;
  if (incoming) await store.destroy(incoming);   // ротація: старий номер тепер мертвий
  const sid = await store.create(user.id);       // новий запис, чистий відлік строку

  res.setHeader("Set-Cookie",
    `sid=${sid}; HttpOnly; Secure; SameSite=Lax; Path=/`);
}

// ВИХІД: спершу гасимо ПРАВДУ у сховищі, і лише потім прибираємо cookie
async function logout(req, res) {
  const sid = parseCookie(req.headers.cookie).sid;
  if (sid) await store.destroy(sid);             // запис мертвий → номер нічого не варт
  res.setHeader("Set-Cookie",
    `sid=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0`);
}
