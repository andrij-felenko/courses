# Калібрування твердого заліза: крутимо пристрій повний оберт, ловимо min/max
class HardIronCalib:
    def __init__(self):
        self.xmin = self.ymin = 32767
        self.xmax = self.ymax = -32768

    def update(self, x, y):   # виклик у циклі під час обертання
        self.xmin = min(self.xmin, x);  self.xmax = max(self.xmax, x)
        self.ymin = min(self.ymin, y);  self.ymax = max(self.ymax, y)

    def heading(self, x, y, declination_deg):
        xoff = (self.xmax + self.xmin) // 2   # центр кола по X = зсув твердого заліза
        yoff = (self.ymax + self.ymin) // 2
        return compass_heading(x - xoff, y - yoff, declination_deg)
