import asyncio
from pymavlink import mavutil

class AsyncCompanionBridge:
    def __init__(self, port: str = "/dev/ttyAMA0", baud: int = 921600):
        self.port = port
        self.baud = baud
        self.master = None
        self.running = False
        self.current_yaw = 0.0

    async def connect(self):
        # Відкриття MAVLink з'єднання через послідовний порт
        self.master = mavutil.mavlink_connection(
            self.port,
            baud=self.baud,
            autoreconnect=True,
            source_system=1,
            source_component=mavutil.mavlink.MAV_COMP_ID_ONBOARD_COMPUTER
        )
        self.running = True
        print(f"З'єднання з {self.port} на {self.baud} бод встановлено.")

    async def rx_loop(self):
        loop = asyncio.get_running_loop()
        while self.running:
            # Читання без блокування основного Event Loop
            msg = await loop.run_in_executor(
                None, self.master.recv_match, False, 0.05
            )
            if msg is not None:
                msg_type = msg.get_type()
                if msg_type == "ATTITUDE":
                    self.current_yaw = msg.yaw
                elif msg_type == "STATUSTEXT":
                    print(f"[FC Log]: {msg.text}")
            await asyncio.sleep(0.001)

    async def hb_loop(self):
        while self.running:
            self.master.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED,
                0,
                mavutil.mavlink.MAV_STATE_ACTIVE
            )
            await asyncio.sleep(1.0) # 1 Гц

    async def tx_setpoint_loop(self):
        # Маска керування вектором швидкості (0x01C7)
        # Ігноруємо X, Y, Z, Ax, Ay, Az
        type_mask = (
            mavutil.mavlink.POSITION_TARGET_TYPEMASK_X_IGNORE |
            mavutil.mavlink.POSITION_TARGET_TYPEMASK_Y_IGNORE |
            mavutil.mavlink.POSITION_TARGET_TYPEMASK_Z_IGNORE |
            mavutil.mavlink.POSITION_TARGET_TYPEMASK_AX_IGNORE |
            mavutil.mavlink.POSITION_TARGET_TYPEMASK_AY_IGNORE |
            mavutil.mavlink.POSITION_TARGET_TYPEMASK_AZ_IGNORE
        )

        while self.running:
            # Уставка: швидкість 1.0 м/с вперед за віссю X (North)
            self.master.mav.set_position_target_local_ned_send(
                0,                               # time_boot_ms
                1,                               # target_system
                1,                               # target_component
                mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                type_mask,
                0.0, 0.0, 0.0,                   # x, y, z
                1.0, 0.0, 0.0,                   # vx, vy, vz (1 м/с вперед)
                0.0, 0.0, 0.0,                   # afx, afy, afz
                0.0, 0.0                         # yaw, yaw_rate
            )
            await asyncio.sleep(0.05) # Строго 20 Гц (50 мс)

    async def run(self):
        await self.connect()
        await asyncio.gather(
            self.rx_loop(),
            self.hb_loop(),
            self.tx_setpoint_loop()
        )

    def stop(self):
        self.running = False
        if self.master:
            self.master.close()


if __name__ == "__main__":
    bridge = AsyncCompanionBridge()
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        bridge.stop()
        print("Python Companion Bridge зупинено.")
