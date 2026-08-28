use core::sync::atomic::{AtomicU32, Ordering};

// Оголошення: глобальний, видний обом ядрам
static EVENTS: AtomicU32 = AtomicU32::new(0);

// Core 0 — збір/мережа: інкремент (Relaxed — потрібна лише атомарність, не порядок)
fn on_data_ready() {
    EVENTS.fetch_add(1, Ordering::Relaxed); // неподільна RMW без замка
}

// Core 1 — loop(): читання свіжого значення
fn loop_iter() {
    let n = EVENTS.load(Ordering::Relaxed); // атомарне читання
    display(n);

    // Для порівняння — те саме спінлоком (надмірно для одного слова):
    // let _g = MUX.lock(); n = EVENTS.load(Ordering::Relaxed) + 1;
}
