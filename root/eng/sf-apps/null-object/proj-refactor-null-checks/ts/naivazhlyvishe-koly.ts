// ПОГАНО: будь-яка відсутність → FREE, обидва баги проковтнуто
function loadBad(row: Row | null): Subscription {
  return row ? new PaidSubscription(row) : FREE;
}

// ДОБРЕ: розвилку проходимо явно, перш ніж підставляти порожній об'єкт
function loadSubscription(userId: string): Subscription {
  const user = users.get(userId);              // кине, якщо юзера немає — це вже не «вільний»
  const row = plans.find(user.planId);         // find кидає на збій запиту, не повертає null

  if (user.tier === "enterprise" && row === null) {
    // enterprise без плану — порушення інваріанта, а не вільний тариф
    throw new Error(`enterprise-акаунт ${userId} без плану — цілісність порушено`);
  }
  return row === null ? FREE : new PaidSubscription(row);   // рядка нема → законно вільний
}
