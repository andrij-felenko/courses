// BFF головного екрана: зібрати один екран із ДВОХ розгортань.
async function homeScreen(homeId: HomeId): Promise<Card[]> {
  const devices = await core.listDevices(homeId);          // синхронно, та сама хмара — дешево
  // останні виміри тепер у СЕРВІСІ телеметрії: мережа, і їй дозволено бути повільною
  const readings = await withFallback(
    () => telemetry.lastReadings(devices.map(d => d.id)),   // ОДИН грубий виклик, не N
    new Map(),                                              // таймаут → показати пристрій без виміру
  );
  return devices.map(d => ({ ...d, lastReading: readings.get(d.id) ?? null }));
}
