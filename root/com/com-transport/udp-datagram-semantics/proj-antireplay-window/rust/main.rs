const BITS: i64 = 64;

#[derive(Clone, Copy, PartialEq, Debug)]
enum Verdict { New, Late, Duplicate, TooOld }

#[derive(Default)]
struct Window {
    top: u32, first: u32, bits: u64, started: bool,
    accepted: u64, lost: u64, duplicate: u64, reordered: u64, too_old: u64,
}

impl Window {
    fn live(&self) -> i64 {
        (self.top.wrapping_sub(self.first) as i64 + 1).min(BITS)
    }

    fn update(&mut self, seq: u32) -> Verdict {
        if !self.started {
            self.started = true;
            self.top = seq;
            self.first = seq;
            self.bits = 1;
            self.accepted = 1;
            return Verdict::New;
        }

        let d = seq.wrapping_sub(self.top) as i32 as i64;

        if d > 0 {
            let live = self.live();
            // checked_shl повертає None замість зсуву на 64 і більше — те, що в C
            // є невизначеною поведінкою, тут стає звичайною гілкою match
            match self.bits.checked_shl(d as u32) {
                Some(shifted) => {
                    let stay = BITS - d;                    // позицій лишається у вікні
                    let fallen = self.bits >> stay;         // d старших позицій
                    let real = (live - stay).max(0);
                    self.lost += (real - fallen.count_ones() as i64) as u64;
                    self.bits = shifted | 1;
                }
                None => {
                    self.lost += (live - self.bits.count_ones() as i64) as u64
                               + (d - BITS) as u64;
                    self.bits = 1;
                }
            }
            self.top = seq;
            self.accepted += 1;
            return Verdict::New;
        }

        if d <= -BITS {
            self.too_old += 1;
            return Verdict::TooOld;
        }

        let k = (-d) as u32;
        let bit = 1u64 << k;
        if self.bits & bit != 0 {
            self.duplicate += 1;
            return Verdict::Duplicate;
        }

        if k as i64 >= self.live() {
            self.first = seq;
        }
        self.bits |= bit;
        self.accepted += 1;
        self.reordered += 1;
        Verdict::Late
    }
}
