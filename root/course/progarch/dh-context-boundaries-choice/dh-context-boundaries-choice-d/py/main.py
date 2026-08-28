# КОНТЕКСТ КЕРУВАННЯ (ядро): пристрій — жива керована річ
@dataclass
class Device:                       # control.Device
    id: DeviceId
    kind: str                       # "lock" | "lamp" | "sensor"
    capabilities: frozenset[str]    # що саме вміє
    state: DeviceState              # поточний стан, яким командуємо
    room: RoomId
    # тут живуть інваріанти: замок не нічий, стан завжди визначений;
    # змінюється, коли з'являється нова радіо-можливість чи тип заліза

# КОНТЕКСТ ТЕЛЕМЕТРІЇ: пристрій — лише джерело ряду вимірів
@dataclass(frozen=True)
class Device:                       # telemetry.Device
    source_id: SourceId
    unit: str                       # "°C", "lux", ...
    retention_days: int
    # ні стану, ні життєвого циклу, ні кімнати — тут це зайве;
    # змінюється, коли міняють retention чи downsampling

# КОНТЕКСТ БІЛІНГУ (загальне): пристрій — рядок тарифу
@dataclass(frozen=True)
class Device:                       # billing.Device
    home_id: HomeId
    counts_against_plan: bool
    active_since: date
    # байдуже, лампа то чи замок — важливо лише рахувати чи ні;
    # змінюється, коли міняють ціни й плани
