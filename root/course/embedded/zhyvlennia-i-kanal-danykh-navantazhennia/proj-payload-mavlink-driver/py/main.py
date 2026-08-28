import asyncio
import time
from pymavlink import mavutil

class MavlinkCameraDriver:
    """Асинхронний драйвер корисного навантаження MAVLink Camera Protocol v2."""

    def __init__(self, connection_str: str = 'udpin:127.0.0.1:14555', sysid: int = 1, compid: int = 100):
        self.sysid = sysid
        self.compid = compid
        self.conn = mavutil.mavlink_connection(connection_str, source_system=self.sysid, source_component=self.compid)
        
        self.image_index = 0
        self.is_capturing = False
        self.capture_interval = 0.0
        self.capture_count = 0
        self.current_zoom = 1.0
        self.start_time = time.monotonic()

    def get_boot_time_ms(self) -> int:
        return int((time.monotonic() - self.start_time) * 1000)

    def get_utc_time_us(self) -> int:
        return int(time.time() * 1_000_000)

    async def heartbeat_loop(self):
        """Регулярна передача Heartbeat з частотою 1 Гц."""
        while True:
            self.conn.mav.heartbeat_send(
                type=mavutil.mavlink.MAV_TYPE_CAMERA,
                autopilot=mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                base_mode=0,
                custom_mode=0,
                system_status=mavutil.mavlink.MAV_STATE_ACTIVE
            )
            await asyncio.sleep(1.0)

    def send_ack(self, command: int, result: int):
        """Надсилання підтвердження COMMAND_ACK ініціатору команди."""
        self.conn.mav.command_ack_send(
            command=command,
            result=result,
            progress=100,
            result_param2=0,
            target_system=self.sysid,
            target_component=mavutil.mavlink.MAV_COMP_ID_ALL
        )

    def send_camera_information(self):
        """Відповідь на запит CAMERA_INFORMATION із параметрами оптичної системи."""
        flags = (
            mavutil.mavlink.CAMERA_CAP_FLAGS_CAPTURE_IMAGE |
            mavutil.mavlink.CAMERA_CAP_FLAGS_CAPTURE_VIDEO |
            mavutil.mavlink.CAMERA_CAP_FLAGS_HAS_BASIC_ZOOM
        )
        self.conn.mav.camera_information_send(
            time_boot_ms=self.get_boot_time_ms(),
            vendor_name=b"AeroSensors Inc.\x00".ljust(32, b'\x00'),
            model_name=b"HawkEye 4K Pro\x00".ljust(32, b'\x00'),
            firmware_version=0x02010000,
            focal_length=35.0,
            sensor_size_h=36.0,
            sensor_size_v=24.0,
            resolution_h=6000,
            resolution_v=4000,
            lens_id=0,
            flags=flags,
            cam_definition_version=1,
            cam_definition_uri=b"http://192.168.1.10/camera_def.xml\x00".ljust(140, b'\x00')
        )

    def trigger_capture(self):
        """Фіксація експонування кадру та передача пакета геотегування."""
        self.image_index += 1
        print(f"[Python-Камера] Спуск затвора! Знімок #{self.image_index}")

        # Генерація пакета зворотного зв'язку CAMERA_IMAGE_CAPTURED
        url = f"http://192.168.1.10/DCIM/IMG_{self.image_index:05d}.JPG".encode('utf-8').ljust(205, b'\x00')
        self.conn.mav.camera_image_captured_send(
            time_utc=self.get_utc_time_us(),
            time_boot_ms=self.get_boot_time_ms(),
            lat=504501000,       # 50.4501°
            lon=305234000,       # 30.5234°
            alt=150000,          # 150.0 м AMSL
            relative_alt=50000,  # 50.0 м над грунтом
            q=[1.0, 0.0, 0.0, 0.0],
            image_index=self.image_index,
            capture_result=1,
            file_url=url
        )

    async def capture_interval_loop(self):
        """Асинхронний таймер серійної інтервальної зйомки."""
        while True:
            if self.is_capturing and self.capture_interval > 0:
                await asyncio.sleep(self.capture_interval)
                if not self.is_capturing:
                    continue
                self.trigger_capture()
                if self.capture_count > 0:
                    self.capture_count -= 1
                    if self.capture_count == 0:
                        self.is_capturing = False
            else:
                await asyncio.sleep(0.05)

    def handle_command_long(self, msg):
        """Диспетчеризація вхідних команд MAVLink."""
        cmd = msg.command

        if cmd == mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE:
            req_msg = int(msg.param1)
            if req_msg == mavutil.mavlink.MAVLINK_MSG_ID_CAMERA_INFORMATION:
                self.send_ack(cmd, mavutil.mavlink.MAV_RESULT_ACCEPTED)
                self.send_camera_information()
            else:
                self.send_ack(cmd, mavutil.mavlink.MAV_RESULT_DENIED)

        elif cmd == mavutil.mavlink.MAV_CMD_IMAGE_START_CAPTURE:
            self.capture_interval = msg.param2
            self.capture_count = int(msg.param3)

            self.send_ack(cmd, mavutil.mavlink.MAV_RESULT_ACCEPTED)
            self.trigger_capture()

            if self.capture_interval > 0 and (self.capture_count > 1 or self.capture_count == 0):
                self.is_capturing = True
                if self.capture_count > 1:
                    self.capture_count -= 1

        elif cmd == mavutil.mavlink.MAV_CMD_IMAGE_STOP_CAPTURE:
            self.is_capturing = False
            self.send_ack(cmd, mavutil.mavlink.MAV_RESULT_ACCEPTED)

        elif cmd == mavutil.mavlink.MAV_CMD_SET_CAMERA_ZOOM:
            self.current_zoom = msg.param2
            print(f"[Python-Камера] Встановлено зум: {self.current_zoom}x")
            self.send_ack(cmd, mavutil.mavlink.MAV_RESULT_ACCEPTED)

        else:
            self.send_ack(cmd, mavutil.mavlink.MAV_RESULT_DENIED)

    async def rx_loop(self):
        """Неблокувальний цикл прийому повідомлень."""
        loop = asyncio.get_running_loop()
        while True:
            msg = await loop.run_in_executor(None, self.conn.recv_match, True)
            if msg:
                if msg.get_type() == 'COMMAND_LONG':
                    if msg.target_system == self.sysid and msg.target_component in (self.compid, 0):
                        self.handle_command_long(msg)
            else:
                await asyncio.sleep(0.005)

    async def run(self):
        print("Запуск асинхронного MAVLink Camera Driver (Python)...")
        await asyncio.gather(
            self.heartbeat_loop(),
            self.rx_loop(),
            self.capture_interval_loop()
        )

if __name__ == '__main__':
    driver = MavlinkCameraDriver()
    try:
        asyncio.run(driver.run())
    except KeyboardInterrupt:
        print("Драйвер зупинено користувачем.")
