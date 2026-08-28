use std::sync::atomic::{AtomicU32, Ordering};

static mut PAYLOAD: u32 = 0;               // звичайні дані — без atomic
static READY: AtomicU32 = AtomicU32::new(0); // прапорець-публікація

// Потік A — виробник
fn produce() {
    unsafe { PAYLOAD = 42; }                       // 1) готуємо дані
    READY.store(1, Ordering::Release);             // 2) публікуємо: release
    // release не дає запису PAYLOAD просочитися ПІСЛЯ цього рядка
}

// Потік B — споживач
fn consume() -> u32 {
    while READY.load(Ordering::Acquire) == 0 {
        // чекаємо публікації; acquire не дає читанню PAYLOAD
        // піднятися ВИЩЕ цієї перевірки
        std::hint::spin_loop();
    }
    unsafe { PAYLOAD }                             // гарантовано вже 42
}
