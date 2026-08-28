# PAL-розгортка: рахунок таймінгу рядка
lines_per_frame = 625
frames_per_sec  = 25.0

line_rate = lines_per_frame * frames_per_sec  # = 15625 рядків/с
line_time = 1.0 / line_rate                   # = 64.0 мкс на рядок

# скільки точок устигне піксельний такт 8 МГц за активну частину рядка
# (з 64 мкс близько 52 мкс — активне відео, решта — синхро + гасіння)
pixel_clock = 8.0e6                     # 8 МГц
active_time = 52.0e-6                    # активна частина рядка, с
dots = int(pixel_clock * active_time)   # = 416 точок уздовж рядка
