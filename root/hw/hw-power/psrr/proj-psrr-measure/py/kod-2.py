class Awg:
    """Генератор синусоїди."""

    def __init__(self, dev):
        self.d = dev
        self.d.write("OUTP1 OFF")
        self.d.write("SOUR1:FUNC SIN")
        self.d.write("SOUR1:VOLT:OFFS 0")
        self.d.write("OUTP1:LOAD 50")

    def set(self, freq, vpp):
        self.d.write("SOUR1:FREQ %.6f" % freq)
        self.d.write("SOUR1:VOLT %.4f" % min(vpp, GEN_VPP_MAX))
        self.d.write("OUTP1 ON")

    def off(self):
        self.d.write("OUTP1 OFF")


class Scope:
    """Двоканальний осцилограф: захопити пару записів."""

    def __init__(self, dev):
        self.d = dev
        self.d.timeout = 30000
        for ch in (1, 2):
            self.d.write(":CHAN%d:DISP ON" % ch)
            self.d.write(":CHAN%d:PROB 1" % ch)      # щуп 1:1 — удесятеро більше сигналу
            self.d.write(":CHAN%d:IMP ONEM" % ch)
            self.d.write(":CHAN%d:COUP AC" % ch)     # інакше 3.3 В з'їдять шкалу
            self.d.write(":CHAN%d:BWL ON" % ch)      # 20 МГц — геть зайвий шум
            self.d.write(":CHAN%d:OFFS 0" % ch)
        self.d.write(":ACQ:TYPE HRES")               # згладжування в залізі + антиаліас
        self.d.write(":TRIG:SOUR CHAN1")
        self.d.write(":TRIG:LEV 0")

    def set_scale(self, ch, volts_pp):
        """Вертикальна шкала: 6 поділок під розмах, у межах приладу."""
        s = min(max(volts_pp / 6.0, 1e-3), 5.0)
        self.d.write(":CHAN%d:SCAL %.6f" % (ch, s))

    def capture(self, f0, cycles):
        self.d.write(":TIM:SCAL %.9f" % (cycles / f0 / 10.0))   # 10 поділок на екран
        self.d.write(":TIM:POS 0")
        self.d.write(":DIG CHAN1,CHAN2")             # блокує, поки не набере
        return self._read(1), self._read(2)

    def _read(self, ch):
        self.d.write(":WAV:SOUR CHAN%d" % ch)
        self.d.write(":WAV:FORM BYTE")
        self.d.write(":WAV:POIN:MODE RAW")
        self.d.write(":WAV:POIN MAX")
        pre = [float(x) for x in self.d.query(":WAV:PRE?").split(",")]
        xinc, yinc, yorg, yref = pre[4], pre[7], pre[8], pre[9]
        raw = self.d.query_binary_values(":WAV:DATA?", datatype="B", container=np.array)
        clipped = bool((raw <= 1).any() or (raw >= 254).any())
        return (raw - yref) * yinc + yorg, xinc, clipped
