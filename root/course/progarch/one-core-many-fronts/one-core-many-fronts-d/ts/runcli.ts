// Точка входу 1: HTTP-контролер із вшитою перевіркою правила
app.post('/api/heating/start', async (req, res) => {
  const { roomId, targetTemperature } = req.body;

  // Доменне правило зашите безпосередньо в обробник запиту
  const openWindows = await db.query(
    'SELECT id FROM windows WHERE room_id = ? AND is_open = true',
    [roomId]
  );
  if (openWindows.length > 0) {
    return res.status(422).json({ error: 'Неможливо увімкнути опалення: вікна відчинені' });
  }

  await db.query(
    'UPDATE climate SET target_temperature = ?, is_heating = true WHERE room_id = ?',
    [targetTemperature, roomId]
  );
  return res.json({ status: 'ok' });
});

// Точка входу 2: консольна утиліта монтажника (CLI)
async function runCli(args: string[]) {
  const [roomId, tempStr] = args;
  const targetTemperature = parseFloat(tempStr);

  // Перевірку вікон пропущено: прямий запис у спільну базу даних
  await db.query(
    'UPDATE climate SET target_temperature = ?, is_heating = true WHERE room_id = ?',
    [targetTemperature, roomId]
  );
  console.log(`Опалення кімнати ${roomId} увімкнено на ${targetTemperature}°C`);
}
