import time
from pymavlink import mavutil

DEVICE   = '/dev/ttyUSB0'   # серійний до контролера; для симулятора: 'udpin:localhost:14550'
LOOP_HZ  = 50               # такт головного циклу
LOOP_DT  = 1.0 / LOOP_HZ

def run(device):
    state = LinkState()
    m = reconnect(device, None, state)  # перше підключення; connect() всередині стамкне heartbeat
    prev_alive = True                   # лінія доведено жива — узгоджено з link_alive()
    own_hb = RateLimiter(hz=1)          # СВІЙ heartbeat раз на секунду

    try:
        while True:
            t0 = time.time()

            # 1) ВИЧЕРПАТИ лінію — забрати все, що накопичилось (не блокує)
            drain_link(m, state)

            # 2) ДЕТЕКТОР ОБРИВУ — судимо за часом heartbeat, не за сокетом
            alive = check_link(m, state, prev_alive)
            prev_alive = alive

            # 3) РЕКОНЕКТ — якщо лінія мертва, підняти її (закривши стару!)
            if not alive:
                m = reconnect(device, m, state)
                prev_alive = True           # connect() знову стамкнув час → лінія жива
                continue                    # такт «згоріло» на реконект — наступний з чистого

            # 4) ВЛАСНІ КОМАНДИ — з обмеженням частоти, лише по живій лінії
            if own_hb.ready():
                # свій heartbeat: показуємо контролеру, що бортовий комп живий
                m.mav.heartbeat_send(
                    mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
                    mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
            maybe_send_setpoint(m, state)   # навігаційні уставки, теж rate-limited

            # 5) ТРИМАТИ ТАКТ — доспати до кінця кроку, не крутити цикл марно
            dt = time.time() - t0
            if dt < LOOP_DT:
                time.sleep(LOOP_DT - dt)

    except KeyboardInterrupt:
        print("\n[EXIT] Ctrl+C — акуратне завершення")
    finally:
        shutdown(m, state)                  # роззброїти (на землі) і закрити лінію


if __name__ == '__main__':
    run(DEVICE)
