# Брама 1 — на краю хмари (шлюз): автентифікація + груба авторизація
def edge_gate(req) -> Subject:
    subject = verify_access_token(req.token)          # підпис локально → суб'єкт, або None
    if subject is None:
        raise Http(401)                               # «не знаю тебе»
    if not policy.may_class(subject, "device.command"):  # об'єкто-НЕЗАЛЕЖне: роль узагалі командує?
        raise Http(403)                               # гість — стоп ТУТ, сервіс не потурбовано
    return subject                                    # несемо доведеного суб'єкта далі

# Брама 2 — у сервісі пристроїв: тонка ОБ'ЄКТНА авторизація
def unlock_door(subject: Subject, door_id: str):
    door = devices.load(door_id)                      # об'єкт У РУКАХ: у ньому home_id
    if not authz.can(subject, "unlock", door):        # «цей замок — у ТВОЄМУ домі?»
        raise Http(403)                               # чужий замок — 403, IDOR закрито
    door.unlock()                                     # обидві брами пройдено → сигнал на хаб
