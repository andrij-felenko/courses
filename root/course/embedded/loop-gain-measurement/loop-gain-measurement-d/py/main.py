# Виміряти петлеве підсилення на одній частоті f_test.
# Вкидаємо синус у керування, корелюємо відгук виходу з тим самим синусом.
from math import sin, cos, pi, log10, atan2

def measure_point(f_test, fs, cycles, amp):
    w = 2.0 * pi * f_test / fs           # фаза за один відлік
    n_samples = int(cycles * fs / f_test)  # ціла к-ть періодів

    acc_i = acc_q = 0.0   # дійсна / уявна частини відгуку
    ref_i = ref_q = 0.0   # те саме для опорного збурення

    for n in range(n_samples):
        s = sin(w * n)
        drive = amp * s                  # мала добавка до керування
        ctrl_inject(drive)               # вкинути в петлю поверх керування

        y = adc_read_output()            # відгук виходу через АЦП
        acc_i += y * sin(w * n)          # кореляція з sin
        acc_q += y * cos(w * n)          # кореляція з cos
        ref_i += drive * sin(w * n)      # те саме для збурення
        ref_q += drive * cos(w * n)

    # Відношення комплексних амплітуд відгук/збурення = L(j2pi f_test)
    out_re, out_im = acc_i, acc_q
    in_re, in_im   = ref_i, ref_q
    den   = in_re * in_re + in_im * in_im
    l_re  = (out_re * in_re + out_im * in_im) / den
    l_im  = (out_im * in_re - out_re * in_im) / den

    mag_db    = 10.0 * log10(l_re * l_re + l_im * l_im)   # 20*log10(|L|) = 10*log10(|L|^2)
    phase_deg = atan2(l_im, l_re) * 57.29578              # 180/pi
    return mag_db, phase_deg
