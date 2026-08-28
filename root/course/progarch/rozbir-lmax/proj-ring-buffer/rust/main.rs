use std::cell::UnsafeCell;
use std::hint;
use std::sync::atomic::{AtomicI64, Ordering};
use std::sync::Arc;

#[repr(align(64))]
struct Padded(AtomicI64);   // кожен лічильник — у своїй лінії кешу

pub struct Ring<T: Copy + Default, const N: usize> {
    cursor: Padded,                 // опубліковано; пише виробник
    gating: Padded,                 // спожито;    пише споживач
    slots:  UnsafeCell<[T; N]>,     // наперед виділені, перевикористовувані
}

// Безпека тримається на дисципліні послідовностей, а не на типах: кожен бік
// лише читає чужий лічильник і пише свій, а доступ до слотів розведено в часі.
unsafe impl<T: Copy + Default, const N: usize> Sync for Ring<T, N> {}

impl<T: Copy + Default, const N: usize> Ring<T, N> {
    const MASK: i64 = (N - 1) as i64;

    pub fn new() -> (Producer<T, N>, Consumer<T, N>) {
        assert!(N.is_power_of_two(), "N мусить бути степенем двійки");
        let ring = Arc::new(Ring {
            cursor: Padded(AtomicI64::new(-1)),
            gating: Padded(AtomicI64::new(-1)),
            slots:  UnsafeCell::new([T::default(); N]),
        });
        // Рівно ОДИН Producer і ОДИН Consumer: жоден не Clone, тож принцип
        // одного письменника вбудовано в самі типи — другого не створити.
        (Producer { ring: ring.clone(), next: 0, cached_gating: -1 },
         Consumer { ring, next_read: 0 })
    }
}

pub struct Producer<T: Copy + Default, const N: usize> {
    ring: Arc<Ring<T, N>>,
    next: i64,            // приватний лічильник — атомарне захоплення НЕ потрібне
    cached_gating: i64,   // кеш стримувальної послідовності
}

impl<T: Copy + Default, const N: usize> Producer<T, N> {
    pub fn publish(&mut self, event: T) {
        let seq = self.next;
        let wrap_point = seq - N as i64;

        // Перезапис слота безпечний лише коли споживач пройшов номер seq−N.
        if wrap_point > self.cached_gating {
            loop {
                let g = self.ring.gating.0.load(Ordering::Acquire);
                if wrap_point <= g { self.cached_gating = g; break; }
                hint::spin_loop();
            }
        }

        // SAFETY: цей слот зараз не читає ніхто — споживач уже за seq−N, а
        // наступні номери ще не опубліковано. Ми — єдиний письменник.
        unsafe { (*self.ring.slots.get())[(seq & Ring::<T, N>::MASK) as usize] = event; }
        self.ring.cursor.0.store(seq, Ordering::Release);   // ПУБЛІКАЦІЯ: release
        self.next = seq + 1;
    }
}

pub struct Consumer<T: Copy + Default, const N: usize> {
    ring: Arc<Ring<T, N>>,
    next_read: i64,
}

impl<T: Copy + Default, const N: usize> Consumer<T, N> {
    pub fn drain(&mut self, mut handle: impl FnMut(T)) -> i64 {
        let available = self.ring.cursor.0.load(Ordering::Acquire);  // одне acquire на пакет
        if available < self.next_read { return 0; }

        let mut s = self.next_read;
        while s <= available {
            // SAFETY: слоти next_read..=available опубліковано (acquire їх побачив),
            // виробник їх не чіпає, поки ми не зрушимо стримувальну послідовність.
            let event = unsafe { (*self.ring.slots.get())[(s & Ring::<T, N>::MASK) as usize] };
            handle(event);
            s += 1;
        }

        let n = available - self.next_read + 1;
        self.next_read = available + 1;
        self.ring.gating.0.store(available, Ordering::Release);   // звільнити пробіг
        n
    }
}
