# Записати параметр WPNAV_SPEED = 800 (см/с) — те саме роблять
# і Mission Planner, і QGroundControl, лише з різних кнопок.
m.mav.param_set_send(
    m.target_system, m.target_component,   # адреса борту з його HEARTBEAT
    b"WPNAV_SPEED",                         # ім'я параметра (до 16 символів)
    800.0,                                  # нове значення
    mavutil.mavlink.MAV_PARAM_TYPE_REAL32)  # тип значення

# Борт підтверджує запис, надіславши PARAM_VALUE з НОВИМ значенням —
# станція (будь-яка) чекає його, щоб переконатися, що зміна лягла.
pv = m.recv_match(type='PARAM_VALUE', blocking=True, timeout=1.0)
if pv is not None and pv.param_id == 'WPNAV_SPEED' and pv.param_value == 800.0:
    pass    # успіх: на борту тепер 800; обидві станції побачать це однаково
