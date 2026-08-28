async function enrollDevice(registry: Registry, hub: Hub, billing: Billing,
                            homeId: string, deviceId: string) {
  const undo: Array<() => Promise<void>> = [];
  try {
    await registry.reserve(deviceId, homeId);   undo.push(() => registry.unreserve(deviceId));
    await hub.pushConfig(homeId, deviceId);      undo.push(() => hub.wipeConfig(homeId, deviceId));
    await billing.startMeter(homeId, deviceId);  undo.push(() => billing.stopMeter(homeId, deviceId));
  } catch (err) {
    for (const step of undo.reverse()) await step();   // компенсації — точно у зворотному порядку
    throw err;
  }
}
