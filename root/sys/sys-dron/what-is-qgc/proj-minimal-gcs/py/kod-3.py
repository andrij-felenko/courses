print('чекаю на серцебиття…')
link.wait_heartbeat()                      # звідси відомі target_system і target_component
print(f'апарат sysid={link.target_system}')

ack, tries, next_try, last_print = None, 0, 0.0, 0.0

while True:
    msg = link.recv_match(blocking=True, timeout=0.2)
    if msg is not None:
        result = apply(msg, state)
        if result is not None:
            ack = result

    now = time.monotonic()
    if ack is None and tries < 5 and now >= next_try:
        link.mav.command_long_send(
            link.target_system, AUTOPILOT,
            mav.MAV_CMD_SET_MESSAGE_INTERVAL,
            tries,                                   # confirmation: 0, 1, 2, …
            mav.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,  # param1: який потік
            500_000,                                 # param2: період, мкс → 2 Гц
            0, 0, 0, 0, 0)
        tries += 1
        next_try = now + 1.0

    if now - last_print >= 1.0:
        last_print = now
        print('{mode:>10}  {arm}  {volts}  {pct}  {lat} {lon}  {alt}  ack={ack}'.format(
            mode=state['mode'],
            arm='ЗБРОЄНО' if state['armed'] else 'роззброєно',
            volts=f"{state['volts']:.1f} В" if state['volts'] is not None else '—',
            pct=f"{state['pct']}%" if state['pct'] is not None else '—',
            lat=f"{state['lat']:.6f}" if state['lat'] is not None else '—',
            lon=f"{state['lon']:.6f}" if state['lon'] is not None else '—',
            alt=f"{state['alt']:.1f} м" if state['alt'] is not None else '—',
            ack=ack))
