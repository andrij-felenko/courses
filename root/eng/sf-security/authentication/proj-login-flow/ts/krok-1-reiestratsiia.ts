import argon2 from "argon2";

const ARGON: argon2.Options = {
  type: argon2.argon2id,
  memoryCost: 19456,   // КіБ → 19 МіБ
  timeCost: 2,         // проходи
  parallelism: 1,
};

async function register(email: string, password: string, db: Db): Promise<void> {
  const norm = email.trim().toLowerCase();
  // хеш уже містить і сіль, і параметри — зберігаємо рядок як є
  const pwHash = await argon2.hash(password, ARGON);
  await db.insertUser({ email: norm, pwHash });
}
