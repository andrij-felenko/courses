from pymavlink import mavutil

CONN = 'udpin:localhost:14550'   # SITL; для реального модему: 'serial:COM5:115200'

m = mavutil.mavlink_connection(CONN)
m.wait_heartbeat()               # доки не прийшов — адреси апарата ще немає
print("апарат на лінії: sys %d, comp %d" % (m.target_system, m.target_component))

while True:
    msg = m.recv_match(blocking=True)
    # …тут твоя логіка: читай телеметрію, вирішуй, шли команди…
