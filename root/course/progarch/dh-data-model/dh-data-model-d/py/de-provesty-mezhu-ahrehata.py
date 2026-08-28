@dataclass
class Home:                                     # окремий МАЛИЙ агрегат
    id: "HomeId"
    owner_id: "UserId"                          # дім не буває без власника
    mode: "HomeMode" = "home"                   # «вдома» | «нікого немає» | «ніч»
    room_ids: list["RoomId"] = field(default_factory=list)
    device_ids: list[DeviceId] = field(default_factory=list)  # лише id, не живі пристрої

    def set_mode(self, m: "HomeMode") -> None:
        self.mode = m                           # міняє СВІЙ стан — і тільки
