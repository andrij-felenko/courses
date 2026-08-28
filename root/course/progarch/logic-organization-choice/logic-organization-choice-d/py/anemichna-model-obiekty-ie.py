# Анемічна модель: об'єкт є, але це мішок полів; правило — у сервісі
class Device:
    def __init__(self):
        self.status = "new"       # поля навстіж
        self.home_id = None

class DeviceService:
    def commission(self, d: Device, home_id):
        if d.status != "new":                # те саме правило — знову ЗЗОВНІ об'єкта
            raise Error("пристрій уже введено в дім")
        d.status = "online"
        d.home_id = home_id
