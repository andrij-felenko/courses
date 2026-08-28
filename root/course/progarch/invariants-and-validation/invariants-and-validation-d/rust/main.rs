/// Об'єкт-значення: поле приватне, єдині двері — parse().
pub struct Celsius(f64);

impl Celsius {
    pub fn parse(raw: f64) -> Result<Celsius, String> {
        if raw.is_nan() {
            return Err("температура — не число".into());
        }
        if !(-50.0..=80.0).contains(&raw) {
            return Err(format!("температура поза межами: {raw}"));
        }
        Ok(Celsius(raw))              // ЄДИНЕ місце, де Celsius народжується
    }
    pub fn value(&self) -> f64 { self.0 }
}

// Ядро бере Celsius, а не f64 — недійсне значення сюди не втрапить.
fn decide_heating(room: &Celsius, target: &Celsius) -> bool {
    room.value() < target.value()     // жодної повторної перевірки
}
