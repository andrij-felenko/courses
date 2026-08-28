function aggregateMonth(hubId: string, rows: Reading[]): Summary {
  // десятки тисяч рядків → перцентилі, ковзні середні, детект аномалій
  const total = rows.reduce((s, r) => s + r.value, 0);  // (роботи на ~900 мс)
  return { hub: hubId, avg: total / rows.length };
}

async function handleControl(cmd: string[], sock: Socket) {
  if (cmd[0] === "aggregate") {
    const hubId = cmd[1];
    const rows = await storage.month(hubId);            // неблокуюче читання — ок
    const summary = aggregateMonth(hubId, rows);        // ОТРУТА: ~900 мс CPU В ЦИКЛІ
    sock.write(JSON.stringify(summary) + "\n");
  }
}
