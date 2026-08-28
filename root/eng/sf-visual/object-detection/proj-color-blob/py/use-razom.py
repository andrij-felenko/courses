def detect_target(min_area):
    frame = camera_capture()             # 1. кадр
    mask = threshold_color(frame)        # 2+3. RGB→HSV→поріг (з wraparound)
    mask = erode3(mask)                  # 4. розмикання: спершу ерозія…
    mask = dilate3(mask)                 #     …тоді дилатація — шум геть
    return find_blob(mask, min_area)     # 5. моменти → центр, площа, рамка

# у керуванні:
#   t = detect_target(40)
#   if t is not None:
#       err_x = t["cx"] - W // 2         # зсув цілі від центру кадру → у курс
#       err_y = t["cy"] - H // 2         # → у тангаж/висоту
#       # площа t["area"] росте → ціль ближчає (груба оцінка дальності)
