@dataclass(frozen=True)
class DeviceDTO:
    id: str
    home_id: str
    serial_number: str
    model_name: str
    device_type: str            # 'sensor' | 'actuator' | 'hub' | 'camera'
    is_online: bool
    firmware_version: str
    reported_state: dict[str, Any]  # Фактичний стан, отриманий від фізичного пристрою
    desired_state: dict[str, Any]   # Бажаний стан, встановлений користувачем або правилом
    last_seen_at: datetime
