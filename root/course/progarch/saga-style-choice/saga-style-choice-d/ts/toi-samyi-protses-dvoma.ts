// ХОРЕОГРАФІЯ: процесу як цілого нема ніде — він розсіяний по обробниках.
on("DeviceReserveRequested", async e => {
  await registry.reserve(e.deviceId, e.homeId);
  emit("DeviceReserved", e);              // хто підхопить — реєстр не знає й знати не хоче
});
on("DeviceReserved", async e => {
  try { await hub.pushConfig(e.homeId, e.deviceId); emit("DeviceConfigured", e); }
  catch { emit("DeviceConfigFailed", e); }  // запускаємо ланцюг компенсацій назад
});
on("DeviceConfigured", async e => {
  await billing.startMeter(e.homeId, e.deviceId);   // останній крок — тиша означає «готово»
});
on("DeviceConfigFailed", async e => {
  await registry.unreserve(e.deviceId);   // компенсація теж їде окремою подією
});
