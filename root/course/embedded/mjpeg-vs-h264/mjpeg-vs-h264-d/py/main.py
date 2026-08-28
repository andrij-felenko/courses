# Оцінка стиснутого бітрейту (біт/с) з параметрів потоку.
def estimate_bitrate(w: int, h: int, fps: int,
                     bits_per_pixel: float, compression_ratio: float) -> int:
    # сирий піксельний потік
    raw = w * h * fps * bits_per_pixel   # біт/с
    return int(raw / compression_ratio)


def choose_stream() -> None:
    # HD, 30 к/с, YUV420 → 12 біт/піксель у середньому
    mjpeg = estimate_bitrate(1280, 720, 30, 12.0, 10.0)
    h264 = estimate_bitrate(1280, 720, 30, 12.0, 100.0)

    print(f"MJPEG: {mjpeg // 1000} kbit/s")   # ~33176
    print(f"H.264: {h264 // 1000} kbit/s")    # ~3317

    # радіоканал тримає, скажімо, 6 Мбіт/с надійно
    link_capacity = 6_000_000
    if mjpeg > link_capacity:
        print("MJPEG не влазить у канал — беремо H.264")
