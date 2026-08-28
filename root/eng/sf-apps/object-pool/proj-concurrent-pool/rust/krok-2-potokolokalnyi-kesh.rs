const BATCH: usize     = 32;               // скільки брати/віддавати гуртом
const CACHE_CAP: usize = 2 * BATCH;        // місткість магазина

struct Magazine { slot: [*mut Conn; CACHE_CAP], n: usize }

thread_local! {                            // ← приватний для потоку: 0 синхронізації
    static MAG: std::cell::RefCell<Magazine> =
        std::cell::RefCell::new(Magazine { slot: [std::ptr::null_mut(); CACHE_CAP], n: 0 });
}

fn acquire() -> *mut Conn {
    MAG.with(|m| {
        let mut mag = m.borrow_mut();
        if mag.n == 0 { refill(&mut mag); }         // порожньо — беремо БАТЧ
        if mag.n == 0 { return grow_or_wait(); }    // геть порожньо
        mag.n -= 1;
        mag.slot[mag.n]                             // ← ГАРЯЧИЙ ШЛЯХ: локальний pop
    })
}

fn release(c: *mut Conn) {
    unsafe { (*c).reset(); }                        // чистимо ДО спільного
    MAG.with(|m| {
        let mut mag = m.borrow_mut();
        if mag.n == CACHE_CAP { flush(&mut mag); }  // повно — віддаємо БАТЧ
        let n = mag.n; mag.slot[n] = c; mag.n += 1; // ← ГАРЯЧИЙ ШЛЯХ: локальний push
    })
}

fn refill(mag: &mut Magazine) {            // один вихід — BATCH об'єктів
    let s = my_shard();
    for _ in 0..BATCH {
        let c = s.free.pop();
        if c.is_null() { break; }
        let n = mag.n; mag.slot[n] = c; mag.n += 1;
    }
}
fn flush(mag: &mut Magazine) {
    let s = my_shard();
    for _ in 0..BATCH {
        mag.n -= 1;
        s.free.push(mag.slot[mag.n]);
    }
}
