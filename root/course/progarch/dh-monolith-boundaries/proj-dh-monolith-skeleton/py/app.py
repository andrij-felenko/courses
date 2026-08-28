# app.py — КОРІНЬ: конструює всі модулі, роздає схеми й шину, реєструє підписки
from ids import Bus
from control import make_control
from twin import make_twin
from telemetry import make_telemetry
from automations import make_automations
from notifications import make_notifications
from identity import make_identity
from billing import make_billing
from video import make_video

def build_app(db, bus: Bus):
    # 1) кожен модуль дістає ЛИШЕ свою схему (і шину, якщо публікує)
    identity      = make_identity(db.schema("identity"))
    twin          = make_twin(db.schema("twin"))
    telemetry     = make_telemetry(db.schema("telemetry"))
    billing       = make_billing(db.schema("billing"))
    notifications = make_notifications(db.schema("notifications"))
    video         = make_video(db.schema("video"))
    control       = make_control(db.schema("control"), bus)   # ← публікує у шину
    automations   = make_automations(twin)                    # ← кличе фасад твіна
    # 2) підписки на DeviceEvent — теж лише тут, в одному видимому місці
    bus.subscribe(telemetry.record)          # вимір у ряд
    bus.subscribe(automations.on_event)      # зважити правила
    bus.subscribe(notifications.on_event)    # чи будити власника
    bus.subscribe(billing.on_event)          # пристрій додано/знято
    return dict(identity=identity, twin=twin, telemetry=telemetry, billing=billing,
                notifications=notifications, video=video, control=control, automations=automations)
