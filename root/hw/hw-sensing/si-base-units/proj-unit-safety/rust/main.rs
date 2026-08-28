// Кожна одиниця — окремий тип-обгортка над f64. Число всередині
// однакове; різними їх робить САМЕ ім'я типу — і компілятор.
#[derive(Clone, Copy)]
struct NewtonSeconds(f64);
#[derive(Clone, Copy)]
struct PoundForceSeconds(f64);

// Єдиний дозволений місток між одиницями — явний перевід із коефіцієнтом.
impl From<PoundForceSeconds> for NewtonSeconds {
    fn from(x: PoundForceSeconds) -> NewtonSeconds {
        NewtonSeconds(x.0 * 4.448222)
    }
}

// Навігація приймає ЛИШЕ ньютон-секунди — це записано в типі аргументу.
fn apply_impulse(j: NewtonSeconds) {
    // ... коригуємо траєкторію, знаючи, що j — точно в Н·с ...
    let _ = j.0;
}

fn main() {
    // apply_impulse(PoundForceSeconds(1.85));      // ← НЕ КОМПІЛЮЄТЬСЯ:
    //   expected `NewtonSeconds`, found `PoundForceSeconds`
    apply_impulse(NewtonSeconds::from(PoundForceSeconds(1.85))); // ✓ перевід явний
    apply_impulse(NewtonSeconds(8.23));                          // ✓ вже в Н·с
}
