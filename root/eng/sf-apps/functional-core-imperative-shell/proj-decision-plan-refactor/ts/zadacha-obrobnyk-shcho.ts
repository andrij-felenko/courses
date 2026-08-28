// ── ДО: рішення й дія намертво сплетені ──
async function handleTransaction(accountId: string, tx: Transaction): Promise<void> {
  const acc = await db.loadAccount(accountId);        // дія: читання

  // ── а тут, упереміш із діями, ховається все рішення ──
  if (tx.amount > acc.dailyLimit) {
    await db.flagTransaction(tx.id, "over-limit");     // дія: запис
    await notifier.push(acc.userId, "Транзакцію відкладено на перевірку");
  }

  const newBalance = acc.balance - tx.amount;
  if (newBalance < 0) {
    await db.freezeAccount(accountId);                 // дія: запис
    await notifier.push(acc.userId, "Рахунок заморожено: недостатньо коштів");
  } else {
    await db.setBalance(accountId, newBalance);        // дія: запис
  }

  await audit.log(`tx ${tx.id} on ${accountId}: amount=${tx.amount}`); // дія: запис
}
