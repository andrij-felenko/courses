pub struct TempRange { min: f64, max: f64 }   // поля приватні для модуля

impl TempRange {
    pub fn new(min: f64, max: f64) -> Result<Self, &'static str> {
        // встановлюємо інваріант: некоректний відрізок узагалі не створити.
        if min > max { return Err("min не може бути більший за max"); }
        Ok(TempRange { min, max })
    }

    pub fn set_min(&mut self, v: f64) -> Result<(), &'static str> {
        if v > self.max { return Err("min не може перевищити max"); }
        self.min = v;                          // зберігаємо інваріант
        Ok(())
    }

    pub fn width(&self) -> f64 { self.max - self.min }   // завжди ≥ 0
}
