# ЄДИНИЙ писар device_card; живиться тією самою шиною, що й усі
class DeviceCardProjector:
    def on_event(self, e: DeviceEvent) -> None:
        # 1) голова картки — раз, коли пристрій уперше побачено:
        #    рядок мусить існувати ДО того, як писати в нього вимір
        if not db.has_card(e.device_id):
            d = control.get_device(e.device_id)   # ОДИН виклик на пристрій за життя
            db.insert_head(e.device_id, e.home_id, d.name, d.room)
        # 2) вимір — просто з події, у вже наявний рядок:
        db.update_reading(e.device_id, e.value, e.unit, e.at)
