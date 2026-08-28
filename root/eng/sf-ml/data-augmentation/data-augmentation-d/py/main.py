import random

# Обрізати значення до діапазону 0…255 (щоб яскравість не «перелилась»)
def clamp8(v):
    if v < 0:
        return 0
    if v > 255:
        return 255
    return v

# Аугментувати кадр НА МІСЦІ: дзеркало + зсув яскравості + шум.
# img — плаский список w*h байтів, рядок за рядком.
def augment(img, w, h):
    # 1) з імовірністю 50% — горизонтальне дзеркало (ярлик збережеться)
    if random.getrandbits(1):
        for y in range(h):
            base = y * w
            for x in range(w // 2):
                # ліве ↔ праве
                img[base + x], img[base + w - 1 - x] = \
                    img[base + w - 1 - x], img[base + x]

    # 2) зсув яскравості на випадкове −40…+40 (імітує різне світло)
    bright = random.randint(-40, 40)

    # 3) кожен піксель: зсув яскравості + невеликий шум −10…+10
    for i in range(w * h):
        noise = random.randint(-10, 10)
        img[i] = clamp8(img[i] + bright + noise)
