# межі 32-бітних типів (у Python int безмежний — тримаємо їх явно)
UINT_MAX = 0xFFFFFFFF
INT_MAX  = 0x7FFFFFFF
INT_MIN  = -0x80000000

# беззнакове a + b  (wrap визначений, але все одно небажаний)
if a > UINT_MAX - b:
    overflow()              # суму НЕ рахуємо
else:
    sum = a + b

# знакове a + b  (та сама переставлена нерівність → ловимо обидві межі)
if b > 0 and a > INT_MAX - b:      overflow()   # переб'є зверху
elif b < 0 and a < INT_MIN - b:    overflow()   # провалиться знизу
else:                              sum = a + b
