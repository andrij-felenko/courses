DEG = math.pi / 180
d = 3 * DEG                                              # неув'язка орієнтації: 3°

fT = reading_body(tilt=d,   a_world=(0.0, 0.0))           # T: нахил, але СПОКІЙ
fP = reading_body(tilt=0.0, a_world=(g*math.sin(d), 0.0)) # P: рівний, але РОЗГІН уперед

print("показ давача (осі тіла):")
print(f"  світ T (нахил, спокій):    f_тіло = ({fT[0]:+.4f}, {fT[1]:+.4f})")
print(f"  світ P (рівний, розгін):   f_тіло = ({fP[0]:+.4f}, {fP[1]:+.4f})")

aT = recover_accel(fT, tilt_hat=0.0)
aP = recover_accel(fP, tilt_hat=0.0)
print("що відновив навігатор (поздовжня, вертикальна):")
print(f"  зі світу T:  a = ({aT[0]:+.4f}, {aT[1]:+.4f})   ← фальшивий розгін!")
print(f"  зі світу P:  a = ({aP[0]:+.4f}, {aP[1]:+.4f})   ← справжній розгін")
