async function buySeat(db: Client, eventId: number) {
  for (let i = 0; i < 5; i++) {                  // кілька спроб
    const { seats, ver } = await readSeats(db, eventId);
    if (seats <= 0) return "sold_out";
    const { rowCount } = await db.query(
      "UPDATE events SET seats_left = seats_left - 1, version = version + 1 " +
      "WHERE id = $1 AND version = $2", [eventId, ver]);
    if (rowCount === 1) return "ok";             // версія збіглася — запис пройшов
  }
  return "too_busy";                             // надто велика конкуренція
}
