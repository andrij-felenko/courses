// TypeScript: один потік, цикл подій. Синхронний applyUpdate неподільний САМ ПО СОБІ —
// але щойно між читанням і записом з'явиться await, гонка вертається:
async applyUpdate(u: Update): Promise<"applied" | "dropped"> {
  const seen = await this.load(u.deviceId);        // ← цикл подій може віддати керування ТУТ
  if (u.version <= seen) return "dropped";
  await this.save(u.deviceId, u.value, u.version); // інший обробник міг уже посунути межу
  return "applied";
}
// Лік: серіалізувати за ключем (черга/мьютекс на пристрій) або — краще — атомарний
// умовний запис у сховищі (див. нижче), щоб між читанням і записом не було зазору.
