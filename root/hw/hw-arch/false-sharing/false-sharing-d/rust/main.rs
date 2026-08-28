// те саме мовою Rust: вирівнювання типу робить ту саму роботу
#[derive(Default)]
#[repr(align(64))]
struct Worker {
    processed: u64,
    dropped: u64,
    last_latency: f64,
}

// розмір теж округлиться до 64, тож сусідній елемент — уже в іншій лінії
let mut workers: Vec<Worker> = (0..n).map(|_| Worker::default()).collect();
