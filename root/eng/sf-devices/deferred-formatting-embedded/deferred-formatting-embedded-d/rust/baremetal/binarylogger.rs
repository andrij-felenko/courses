#![no_std]
use core::sync::atomic::{AtomicUsize, Ordering};

pub const BUFFER_SIZE: usize = 1024;
const BUFFER_MASK: usize = BUFFER_SIZE - 1;

pub struct BinaryLogger {
    storage: [u8; BUFFER_SIZE],
    head: AtomicUsize,
    tail: AtomicUsize,
    dropped: AtomicUsize,
}

impl BinaryLogger {
    pub const fn new() -> Self {
        Self {
            storage: [0u8; BUFFER_SIZE],
            head: AtomicUsize::new(0),
            tail: AtomicUsize::new(0),
            dropped: AtomicUsize::new(0),
        }
    }

    pub fn log_event(&mut self, event_id: u16, payload: &[u8]) -> bool {
        let total_len = 2 + 1 + payload.len();
        let current_head = self.head.load(Ordering::Relaxed);
        let current_tail = self.tail.load(Ordering::Acquire);

        if BUFFER_SIZE - (current_head.wrapping_sub(current_tail)) < total_len {
            self.dropped.fetch_add(1, Ordering::Relaxed);
            return false;
        }

        self.head.store(current_head.wrapping_add(total_len), Ordering::Release);

        /* Запис дескриптора події */
        self.storage[current_head & BUFFER_MASK] = (event_id & 0xFF) as u8;
        self.storage[(current_head + 1) & BUFFER_MASK] = ((event_id >> 8) & 0xFF) as u8;
        self.storage[(current_head + 2) & BUFFER_MASK] = payload.len() as u8;

        /* Запис тіла корисного навантаження */
        let mut idx = current_head + 3;
        for &byte in payload {
            self.storage[idx & BUFFER_MASK] = byte;
            idx += 1;
        }

        true
    }
}
