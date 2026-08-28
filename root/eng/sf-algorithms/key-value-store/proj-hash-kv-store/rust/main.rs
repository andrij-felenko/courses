const FNV_OFFSET: u32 = 2166136261;
const FNV_PRIME: u32 = 16777619;
const INIT_CAP: usize = 8; // степінь двійки

pub struct Map {
    // ланцюжок — вектор пар, а не список на вказівниках: пари кошика лежать
    // поспіль, тож прохід ланцюжком — це прохід суцільною пам'яттю
    buckets: Vec<Vec<(String, i64)>>,
    n: usize,
}

fn hash(key: &str) -> u32 {
    let mut h = FNV_OFFSET;
    for b in key.as_bytes() {
        h ^= *b as u32;
        h = h.wrapping_mul(FNV_PRIME); // переповнення тут навмисне, не помилка
    }
    h ^ (h >> 16)
}

impl Map {
    pub fn new() -> Self {
        Map { buckets: vec![Vec::new(); INIT_CAP], n: 0 }
    }

    fn index(&self, h: u32) -> usize { h as usize & (self.buckets.len() - 1) }

    pub fn get(&self, key: &str) -> Option<&i64> {
        let i = self.index(hash(key));
        self.buckets[i]
            .iter()
            .find(|(k, _)| k == key) // звіряємо ПОВНИЙ ключ
            .map(|(_, v)| v)
    }

    pub fn put(&mut self, key: &str, val: i64) {
        let i = self.index(hash(key));
        if let Some(slot) = self.buckets[i].iter_mut().find(|(k, _)| k == key) {
            slot.1 = val; // оновлення наявного: n НЕ росте
            return;
        }
        self.buckets[i].push((key.to_string(), val));
        self.n += 1;
        if 4 * self.n > 3 * self.buckets.len() {
            self.grow();
        }
    }

    pub fn remove(&mut self, key: &str) -> bool {
        let i = self.index(hash(key));
        match self.buckets[i].iter().position(|(k, _)| k == key) {
            // порядок усередині кошика не значить нічого,
            // тож викидаємо за O(1), не зсуваючи хвіст
            Some(p) => { self.buckets[i].swap_remove(p); self.n -= 1; true }
            None => false,
        }
    }

    fn grow(&mut self) {
        let new_cap = self.buckets.len() * 2; // рахуємо ДО того, як позичимо buckets
        let old = std::mem::replace(&mut self.buckets, vec![Vec::new(); new_cap]);
        for chain in old {
            for (k, v) in chain {
                let i = self.index(hash(&k)); // індекс — за НОВОЮ місткістю
                self.buckets[i].push((k, v));
            }
        }
        // self.n не чіпаємо
    }

    pub fn len(&self) -> usize { self.n }
}
