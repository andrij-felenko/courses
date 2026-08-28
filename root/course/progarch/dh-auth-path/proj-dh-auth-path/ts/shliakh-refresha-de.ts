// ── Шлях рефреша на шлюзі: ТУТ виключеному членові кажуть «ні» ──
async function refresh(req: Request): Promise<{ access: string }> {
  const refreshId = readRefreshCookie(req);
  const record = await refreshStore.get(refreshId);   // непрозорий id → правда в сторі
  if (!record) throw new Http(401);                    // refresh відкликано/протух → нового access не дамо

  if (await revocations.isRevoked(record.subjectId, record.homeId))  // виключений із дому?
    throw new Http(403);                               // орган відкликання каже «ні» — за секунди, не за добу

  return { access: issueAccess(record) };              // інакше — свіжий короткий access, ще на кілька хвилин
}
