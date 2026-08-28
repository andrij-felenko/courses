# Кут нахилу: ловимо повідомлення ATTITUDE (радіани).
msg = master.recv_match(type='ATTITUDE', blocking=True, timeout=2)
if msg:
    print(f"крен={msg.roll:+.2f}  тангаж={msg.pitch:+.2f}  курс={msg.yaw:+.2f}")

# Висота й координати: GLOBAL_POSITION_INT (ціле × 1000 чи × 1e7).
pos = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=2)
if pos:
    print(f"висота={pos.relative_alt/1000:.1f} м  "
          f"шир={pos.lat/1e7:.6f}  довг={pos.lon/1e7:.6f}")
