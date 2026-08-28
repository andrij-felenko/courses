// Rust: кожна фаза — окремий ТИП. Метод `hipot` існує лише на `Station<InsulOk>`,
// тож «гіпот без опору ізоляції» — помилка КОМПІЛЯЦІЇ, а не сюрприз на стенді.
use core::marker::PhantomData;

struct GroundOk;
struct InsulOk;
struct Station<S> { hv: Hv, _s: PhantomData<S> }

impl Station<GroundOk> {
    // Пройти опір ізоляції можна лише звідси; успіх ВИДАЄ новий тип-стан.
    fn insulation(self, r_meg: f32) -> Result<Station<InsulOk>, Fail> {
        if r_meg > 10.0 { Ok(Station { hv: self.hv, _s: PhantomData }) }
        else            { Err(Fail::Insulation) }
    }
}

impl Station<InsulOk> {
    // `hipot` НЕ існує ніде, крім цього impl — раніше його не викликати.
    fn hipot(self, v: u16, dwell_ms: u32) -> Charged {
        self.hv.ramp_dwell(v, dwell_ms)
    }
}

// `Charged` неможливо «забути»: єдиний спосіб його позбутися — знищення,
// а воно ЗАВЖДИ розряджає — навіть на ранньому return чи паніці.
struct Charged { hv: Hv }
impl Charged {
    fn leakage(&mut self) -> f32 { self.hv.read_leak() }
}
impl Drop for Charged {
    fn drop(&mut self) { self.hv.bleed_until(50); }   // страж розряду
}
