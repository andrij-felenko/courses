// app.ts — КОРІНЬ: конструює всі модулі, роздає схеми й шину, реєструє підписки
import { Bus } from "./ids";
import { makeControl } from "./control";
import { makeTwin } from "./twin";
import { makeTelemetry } from "./telemetry";
import { makeAutomations } from "./automations";
import { makeNotifications } from "./notifications";
import { makeIdentity } from "./identity";
import { makeBilling } from "./billing";
import { makeVideo } from "./video";

export function buildApp(db: Db, bus: Bus) {
  // 1) кожен модуль дістає ЛИШЕ свою схему (і шину, якщо публікує)
  const identity      = makeIdentity(db.schema("identity"));
  const twin          = makeTwin(db.schema("twin"));
  const telemetry     = makeTelemetry(db.schema("telemetry"));
  const billing       = makeBilling(db.schema("billing"));
  const notifications = makeNotifications(db.schema("notifications"));
  const video         = makeVideo(db.schema("video"));
  const control       = makeControl(db.schema("control"), bus);   // ← публікує у шину
  const automations   = makeAutomations(twin);                    // ← кличе фасад твіна
  // 2) підписки на DeviceEvent — теж лише тут, в одному видимому місці
  bus.subscribe(telemetry.record);          // вимір у ряд
  bus.subscribe(automations.onEvent);       // зважити правила
  bus.subscribe(notifications.onEvent);     // чи будити власника
  bus.subscribe(billing.onEvent);           // пристрій додано/знято
  return { identity, twin, telemetry, billing, notifications, video, control, automations };
}
