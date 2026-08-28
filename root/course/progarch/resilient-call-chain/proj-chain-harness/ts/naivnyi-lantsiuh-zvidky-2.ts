async function runStorm() {
  cCalls = 0;
  // C, що завжди відповідає минущою помилкою — кожна спроба «варта повтору».
  const alwaysFail: Call = async () => {
    cCalls++;
    return { ok: false, kind: "overloaded", retryable: true, latency: 300 };
  };
  const chain: Call = (ctx) =>
    retryNaive(() => retryNaive(() => retryNaive(() => alwaysFail(ctx), 3), 3), 3);
  await chain({ now: 0, deadline: 1e9 });
  console.log(`шторм: C дістав ${cCalls} викликів`);   // → 27
}
