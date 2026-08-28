async function calculateTotalBalance(userId: string): Promise<number> {
  try {
    const profile = await fetchProfile(userId);
    let total = 0;
    for (const accId of profile.accountIds) {
      const balance = await fetchAccountBalance(accId);
      total += balance;
    }
    return total;
  } catch (err) {
    console.error("Помилка розрахунку:", err);
    return 0;
  }
}
