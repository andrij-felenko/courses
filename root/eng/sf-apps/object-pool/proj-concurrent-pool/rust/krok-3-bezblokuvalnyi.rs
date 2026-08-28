use std::sync::atomic::{AtomicPtr, Ordering};
use std::ptr;

pub struct Conn {
    // ... справжні поля ...
    next_free: *mut Conn,                  // ← лінк вільного списку живе в об'єкті
}

pub struct LockFreeStack { head: AtomicPtr<Conn> }

impl LockFreeStack {
    pub fn new() -> Self { Self { head: AtomicPtr::new(ptr::null_mut()) } }

    pub fn push(&self, n: *mut Conn) {
        let mut old = self.head.load(Ordering::Relaxed);
        loop {
            unsafe { (*n).next_free = old; }             // готуємо ланку
            match self.head.compare_exchange_weak(
                old, n,
                Ordering::Release,                       // успіх: ПУБЛІКУЄМО n (крок 4)
                Ordering::Relaxed,                       // невдача: перечитали old
            ) {
                Ok(_)   => return,
                Err(cur) => old = cur,
            }
        }
    }

    pub fn pop(&self) -> *mut Conn {
        let mut old = self.head.load(Ordering::Acquire);
        while !old.is_null() {
            let next = unsafe { (*old).next_free };      // безпечно: пул вузол НЕ звільняє
            match self.head.compare_exchange_weak(
                old, next,
                Ordering::Acquire,                       // успіх: бачимо опубліковане
                Ordering::Acquire,
            ) {
                Ok(_)   => return old,
                Err(cur) => old = cur,
            }
        }
        ptr::null_mut()
    }
}
