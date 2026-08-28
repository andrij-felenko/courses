// Cargo: serde_json. Newtype-обгортки стережуть інваріанти самі.
use serde_json::Value;

// ── Помилка поля — значення, яке повертають, а не паніка ──
#[derive(Debug, PartialEq)]
pub struct FieldError { pub field: &'static str, pub message: String }

// ── Newtype-об'єкти-значення: приватне поле → єдині двері parse() ──
pub struct DeviceId(String);
impl DeviceId {
    pub fn parse(v: Option<&Value>) -> Result<DeviceId, String> {
        let s = v.and_then(Value::as_str).ok_or("очікувано рядок")?;
        if s.is_empty() { return Err("порожній".into()); }
        if s.len() > 32 { return Err("задовгий (>32)".into()); }
        if !s.bytes().all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'-') {
            return Err("лише a–z, 0–9 та дефіс".into());
        }
        Ok(DeviceId(s.to_owned()))
    }
}

pub struct Celsius(f64);
impl Celsius {
    pub fn parse(v: Option<&Value>) -> Result<Celsius, String> {
        let n = v.and_then(Value::as_f64).ok_or("не число")?;
        if !(-50.0..=80.0).contains(&n) {
            return Err(format!("поза межами −50…80: {n}"));
        }
        Ok(Celsius(n))
    }
    pub fn value(&self) -> f64 { self.0 }
}

// Тип-сума: рівно один із дозволених режимів.
#[derive(Debug, PartialEq)]
pub enum Action { Heat, Cool, Off }
impl Action {
    pub fn parse(v: Option<&Value>) -> Result<Action, String> {
        match v.and_then(Value::as_str) {
            Some("heat") => Ok(Action::Heat),
            Some("cool") => Ok(Action::Cool),
            Some("off")  => Ok(Action::Off),
            Some(other)  => Err(format!("невідома дія «{other}»; дозволені: heat, cool, off")),
            None         => Err("очікувано рядок".into()),
        }
    }
}
