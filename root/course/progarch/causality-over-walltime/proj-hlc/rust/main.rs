const MAX_OFFSET_MS: i64 = 500; // терпимий відрив чужого годинника вперед
const C_MAX: u32 = 1 << 16;     // 16 бітів під лічильник

pub enum HlcError { TooFarAhead, CounterOverflow }

/// Гібридний годинник одного вузла. Мітка = пара (l, c).
pub struct Hlc<F: FnMut() -> i64> {
    l: i64,  // фізична частина: настінний час, мс від епохи
    c: u32,  // лічильник, росте лише коли l не зрушив
    phys: F, // джерело настінного часу
}

impl<F: FnMut() -> i64> Hlc<F> {
    pub fn new(phys: F) -> Self { Self { l: 0, c: 0, phys } }

    /// Локальна подія або відправлення — одне правило.
    pub fn now(&mut self) -> Result<(i64, u32), HlcError> {
        let l_prev = self.l;
        self.l = l_prev.max((self.phys)());
        self.c = if self.l == l_prev { self.c + 1 } else { 0 };
        self.guard()
    }

    /// Отримання повідомлення з міткою (l_m, c_m).
    pub fn update(&mut self, l_m: i64, c_m: u32) -> Result<(i64, u32), HlcError> {
        let pt = (self.phys)();
        if l_m > pt + MAX_OFFSET_MS {
            return Err(HlcError::TooFarAhead); // не отруюємо свій l чужим годинником
        }
        let l_prev = self.l;
        self.l = l_prev.max(l_m).max(pt);
        self.c = if self.l == l_prev && self.l == l_m {
            self.c.max(c_m) + 1
        } else if self.l == l_prev {
            self.c + 1
        } else if self.l == l_m {
            c_m + 1
        } else {
            0 // self.l == pt — фізичний обігнав усіх
        };
        self.guard()
    }

    fn guard(&self) -> Result<(i64, u32), HlcError> {
        if self.c >= C_MAX { Err(HlcError::CounterOverflow) } else { Ok((self.l, self.c)) }
    }
}

/// Порядок міток: спершу за l, потім за c (кортеж — лексикографічно).
pub fn less(a: (i64, u32), b: (i64, u32)) -> bool { a < b }
