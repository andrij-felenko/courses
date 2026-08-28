import argon2 from "argon2";

// ESM: рахуємо фіктивний хеш один раз під час старту, з ТИМИ САМИМИ параметрами
const DUMMY_HASH = await argon2.hash("dummy-password-never-matches", ARGON);

async function login(email: string, password: string, db: Db): Promise<User | null> {
  const norm = email.trim().toLowerCase();
  const user = await db.findUser(norm);
  // немає користувача → усе одно звіряємо проти фіктивного хешу:
  // стільки ж часу, те саме повідомлення — існування акаунта не витікає
  const hash = user?.pwHash ?? DUMMY_HASH;
  const ok = await argon2.verify(hash, password);   // звірка за сталий час
  return ok && user ? user : null;
}
