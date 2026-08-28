// Варіант «очікування» замість негайного 409: коротко опитуємо ключ до дедлайну.
async function waitForResult(db, key, userId, path, deadlineMs = 3000): Promise<Stored | null> {
  const until = Date.now() + deadlineMs;
  while (Date.now() < until) {
    const row = await getRow(db, key, userId, path);
    if (row.state === "completed") return toStored(row);   // переможець дописав
    await sleep(100);                                      // 100 мс і ще раз
  }
  return null;                                             // не дочекались — назад до 409
}
