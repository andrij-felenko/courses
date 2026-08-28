from pymavlink import mavutil

link = mavutil.mavlink_connection("udpin:0.0.0.0:14550")
hb = link.wait_heartbeat()
tgt = (link.target_system, link.target_component)

# ArduPilot нумерує записи з одиниці, решта — з нуля;
# ознаки в самому протоколі логу немає, тож дивимося на тип прошивки
id_offset = 1 if hb.autopilot == mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA else 0

# ── 1. Перелік записів
link.mav.log_request_list_send(*tgt, 0, 0xffff)

entries = {}
while True:
    e = link.recv_match(type="LOG_ENTRY", blocking=True, timeout=5)
    if e is None:
        break
    if e.num_logs == 0:            # записів немає — це вся відповідь
        break
    entries[e.id - id_offset] = (e.size, e.time_utc or None)
    if len(entries) == e.num_logs:
        break

if not entries:
    raise SystemExit("на борту немає записів")

# ── 2. Тіло одного запису; size — ОЦІНКА, не критерій завершення
index, (size, _) = sorted(entries.items())[0]
link.mav.log_request_data_send(*tgt, index + id_offset, 0, size)

with open("flight.bin", "wb") as out:
    while True:
        d = link.recv_match(type="LOG_DATA", blocking=True, timeout=5)
        if d is None or d.count == 0:      # таймер або оголошений кінець
            break
        out.seek(d.ofs)
        out.write(bytes(d.data[:d.count]))  # хвіст масиву — нулі доповнення

# ── 3. Повернути апаратові право писати власний журнал
link.mav.log_request_end_send(*tgt)
