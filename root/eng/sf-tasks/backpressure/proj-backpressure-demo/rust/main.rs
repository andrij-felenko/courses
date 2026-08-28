use std::sync::mpsc::{channel, sync_channel};
use std::thread;

// Стеля: sync_channel(32) — send() у повну чергу присипляє нитку.
// (sync_channel(0) — стеля нуль: передача з рук у руки, виробник
//  чекає особисто на споживача, між ними не лежить нічого.)
let (tx, rx) = sync_channel::<Job>(32);

thread::spawn(move || {
    for job in source {
        tx.send(job).unwrap(); // ← на повній черзі нитка засинає тут
    }
});

for job in rx {  // ітератор бере по одному; на порожній черзі — чекає
    handle(job); // повільна ланка: вона й диктує темп усього конвеєра
}

// Двійник: channel() — та сама черга, але БЕЗ стелі. send() той самий,
// тільки він ніколи не чекає: черга росте, доки є пам'ять.
let (tx_unbounded, rx_unbounded) = channel::<Job>();
