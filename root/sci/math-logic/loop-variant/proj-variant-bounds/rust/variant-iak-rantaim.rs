use std::fmt::Debug;

/// Строгий спад + дно + збіг із передбаченою межею.
struct Variant<V: Ord + Debug> {
    floor: V,
    budget: Option<usize>,
    prev: Option<V>,
    steps: usize,
}

impl<V: Ord + Debug> Variant<V> {
    fn new(floor: V, budget: Option<usize>) -> Self {
        Variant { floor, budget, prev: None, steps: 0 }
    }

    /// Викликати ПЕРШИМ рядком тіла циклу — жодна гілка не прослизне.
    fn step(&mut self, now: V) {
        self.steps += 1;
        assert!(now >= self.floor, "варіант пробив дно: {:?} < {:?}", now, self.floor);
        if let Some(prev) = &self.prev {
            assert!(now < *prev, "варіант не впав: {:?} → {:?}", prev, now);
        }
        if let Some(b) = self.budget {
            assert!(self.steps <= b, "перевищено передбачену межу: {} > {}", self.steps, b);
        }
        self.prev = Some(now);
    }
}
