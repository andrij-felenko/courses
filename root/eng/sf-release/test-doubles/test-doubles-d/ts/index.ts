interface Users {
  findByEmail(email: string): Promise<User | undefined>;
  save(user: User): Promise<void>;     // справжня база: кидає UniqueViolation
}

class InMemoryUsers implements Users {             // ФЕЙК
  private readonly rows = new Map<string, User>();
  async findByEmail(email: string) { return this.rows.get(email); }
  async save(user: User) { this.rows.set(user.email, user); }   // тихо перезапише
}

async function register(email: string, users: Users): Promise<User> {
  if (await users.findByEmail(email)) throw new EmailTaken(email);
  const user = { id: newId(), email };
  await users.save(user);              // між перевіркою і записом — вікно
  return user;
}
