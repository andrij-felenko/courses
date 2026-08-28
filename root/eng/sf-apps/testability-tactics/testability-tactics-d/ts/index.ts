function splitEvenly(totalCents: number, parts: number): number[] {
  const base = Math.floor(totalCents / parts);
  const shares = new Array(parts).fill(base);
  const remainder = totalCents - base * parts;      // копійки, що не поділилися
  for (let i = 0; i < remainder; i++) shares[i] += 1;
  // ПОСТУМОВА: скільки взяли, стільки й роздали — інакше падаємо ТУТ
  const sum = shares.reduce((a, b) => a + b, 0);
  if (sum !== totalCents) throw new Error(`втрачено ${totalCents - sum} копійок`);
  return shares;
}
