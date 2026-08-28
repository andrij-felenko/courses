function buildApp(db: Db, bus: Bus) {
  const identity = makeIdentity(db.schema("identity"));
  const twin = makeTwin(db.schema("twin"));
  const telemetry = makeTelemetry(db.schema("telemetry"));
  const control = makeControl(db.schema("control"), bus);   // публікує у шину
  const automations = makeAutomations(twin);                 // кличе фасад твіна
  bus.subscribe(telemetry.record);                           // підписки — теж тут
  bus.subscribe(automations.onEvent);
  return { identity, twin, telemetry, control, automations };
}
