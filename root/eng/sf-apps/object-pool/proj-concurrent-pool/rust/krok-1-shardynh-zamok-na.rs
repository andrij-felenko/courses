use std::sync::atomic::AtomicPtr;

const SHARDS: usize = 64;                   // степінь двійки → маска замість %

#[repr(align(64))]                          // ← кожен шард на своєму рядку кеша (крок 6)
struct Shard {
    free: LockFreeStack,                    // список вільних
}
static SHARDS_ARR: [Shard; SHARDS] = /* ініціалізація */ todo!();

#[inline]
fn my_shard() -> &'static Shard {
    let cpu = unsafe { libc::sched_getcpu() } as usize;   // підказка
    &SHARDS_ARR[cpu & (SHARDS - 1)]
}
