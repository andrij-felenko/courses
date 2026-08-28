use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

let t0 = Instant::now();
// ... робота ...
let elapsed: Duration = t0.elapsed();            // ніколи не від'ємний

let deadline = t0 + Duration::from_secs(30);
let left = deadline.saturating_duration_since(Instant::now());

let stamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
