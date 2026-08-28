from pymavlink import mavutil

log = mavutil.mavlink_connection("2026-08-02 12-00-00.tlog")
while True:
    msg = log.recv_match(blocking=False)
    if msg is None:                      # кінець файлу
        break
    if msg.get_type() == "BAD_DATA":     # ресинхронізація після сміття
        continue
    print(f"{msg._timestamp:.3f}  {msg.get_srcSystem():3d}/{msg.get_srcComponent():<3d}  {msg.get_type()}")
