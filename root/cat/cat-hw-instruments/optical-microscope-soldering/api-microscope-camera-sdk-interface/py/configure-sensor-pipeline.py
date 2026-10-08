import math
from camera_inspection_sdk import CameraDevice

def configure_sensor_pipeline(camera: CameraDevice):
    # Динамічне програмування витримки та аналогового підсилення
    camera.set_parameter("ExposureTimeUs", 2500.0)
    camera.set_parameter("GainDb", 6.0)

    # Програмування зони інтересу ROI (X, Y, W, H)
    camera.set_roi(offset_x=128, offset_y=128, width=1024, height=768)

    # Режим об'єднання пікселів для зниження шуму
    camera.set_binning_mode("SUM_2X2")

    # Генерирування та завантаження таблиці LUT
    lut_data = [int(math.sqrt(i / 4095.0) * 4095.0) for i in range(4096)]
    camera.write_lut(lut_data)
