btns = [Button(2), Button(3), Button(4)]

for b in btns:
    b.begin()                       # кожна визначить свою полярність окремо

while True:
    for b in btns:
        b.update()                  # кожній — свій update щопрохід
    if btns[0].pressed():    ...    # ...
    if btns[1].long_press(): ...    # ...
