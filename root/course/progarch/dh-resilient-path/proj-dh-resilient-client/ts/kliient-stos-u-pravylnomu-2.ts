const telemetry = new ServiceClient("telemetry", resolve, http,
  { pool: 10, queue: 0,  wait: 0,   timeout: 3000, tries: 2, failsToOpen: 5,  cooldown: 2000 }); // fail-fast
const core = new ServiceClient("core", resolve, http,
  { pool: 40, queue: 40, wait: 200, timeout: 1000, tries: 2, failsToOpen: 10, cooldown: 1000 }); // коротка черга

// ЧИТАННЯ: телеметрія — прикраса, тож у неї є ЧЕСНИЙ фолбек. Список пристроїв критичний — фолбека нема.
async function mainScreen(userId: string) {
  const [devices, readings] = await Promise.all([
    core.call<Device[]>("/listDevices", { userId }),                 // свій пул; впаде — екран чесно не збереться
    telemetry.call<Reading[]>("/lastReadings", { userId })
      .catch(() => [] as Reading[]),                                 // ← фолбек: без виміру
  ]);
  const byId = new Map(readings.map((r) => [r.deviceId, r]));
  return devices.map((d) => ({ device: d, reading: byId.get(d.id) ?? null })); // null → плитка «—»
}

// КОМАНДА: той самий стос стійкості — але БЕЗ .catch. Не дотягнулись — помилка летить нагору,
// UI покаже «не вдалося, спробуйте ще», а не збреше «зачинено». Повтор безпечний, бо команда ідемпотентна.
async function lockDoor(deviceId: string): Promise<LockResult> {
  return core.call<LockResult>("/command", { deviceId, op: "lock" });
}
