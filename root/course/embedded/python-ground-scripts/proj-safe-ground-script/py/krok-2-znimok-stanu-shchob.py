import time
from pymavlink import mavutil


class Vehicle:
    """Живий знімок стану апарата — рівно те, що треба для безпечного виходу."""
    def __init__(self):
        self.armed = False           # презумпція: роззброєно, поки не почули інше
        self.rel_alt_m = 0.0         # висота над точкою зльоту, м
        self.last_heartbeat = None   # коли востаннє чули апарат (None = ще ні разу)

    def on_message(self, msg):
        """Одне місце, куди сходяться всі вхідні — тут народжується знімок стану."""
        t = msg.get_type()
        if t == 'HEARTBEAT':
            self.last_heartbeat = time.time()
            self.armed = bool(msg.base_mode
                              & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
        elif t == 'GLOBAL_POSITION_INT':
            self.rel_alt_m = msg.relative_alt / 1000.0    # мм → м

    def on_ground(self):
        """Груба, але надійна ознака «на землі»: майже нульова відносна висота."""
        return self.rel_alt_m < 0.5

    def link_alive(self):
        """Лінія жива, лише якщо heartbeat приходив і не замовк надовго."""
        if self.last_heartbeat is None:
            return False
        return (time.time() - self.last_heartbeat) < 3.0
