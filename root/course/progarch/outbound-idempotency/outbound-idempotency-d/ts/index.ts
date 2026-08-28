// ❌ НЕПРАВИЛЬНО: Новий UUID на кожну спробу ретраю!
for (let attempt = 0; attempt < 3; attempt++) {
  const response = await fetch("https://api.stripe.com/v1/charges", {
    method: "POST",
    headers: {
      "Idempotency-Key": crypto.randomUUID(), // Руйнує ідемпотентність!
    },
    body: JSON.stringify({ amount: 120 }),
  });
}
