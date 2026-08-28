//! Жорсткий декодер LDPC: перевертання бітів.
//! H живе як два пласкі CSR-списки — нулі матриці не зберігаємо взагалі.

use std::cmp::Reverse;

pub struct Ldpc {
    n: usize,
    chk_ptr: Vec<usize>,
    chk_bit: Vec<usize>, // перевірка -> її біти
    bit_ptr: Vec<usize>,
    bit_chk: Vec<usize>, // біт -> його перевірки
}

impl Ldpc {
    /// `checks[j]` — індекси бітів, які накриває перевірка j.
    pub fn new(n: usize, checks: &[Vec<usize>]) -> Self {
        let mut chk_ptr = Vec::with_capacity(checks.len() + 1);
        let mut chk_bit = Vec::new();
        chk_ptr.push(0);
        for bits in checks {
            chk_bit.extend_from_slice(bits);
            chk_ptr.push(chk_bit.len());
        }

        let mut bit_ptr = vec![0usize; n + 1];
        for bits in checks {
            for &i in bits {
                bit_ptr[i + 1] += 1; // ступені бітів
            }
        }
        for i in 0..n {
            bit_ptr[i + 1] += bit_ptr[i]; // префіксна сума -> зсуви
        }

        let mut fill = bit_ptr[..n].to_vec();
        let mut bit_chk = vec![0usize; chk_bit.len()];
        for (j, bits) in checks.iter().enumerate() {
            for &i in bits {
                bit_chk[fill[i]] = j;
                fill[i] += 1;
            }
        }

        Ldpc { n, chk_ptr, chk_bit, bit_ptr, bit_chk }
    }

    fn syndrome(&self, w: &[u8]) -> Vec<u8> {
        self.chk_ptr
            .windows(2)
            .map(|p| self.chk_bit[p[0]..p[1]].iter().fold(0u8, |a, &i| a ^ w[i]))
            .collect()
    }

    /// Править `w` на місці. Повертає (число ітерацій, чи H·ŵᵀ = 0).
    pub fn decode(&self, w: &mut [u8], max_iter: usize) -> (usize, bool) {
        let mut s = self.syndrome(w);

        for it in 0..max_iter {
            if s.iter().all(|&x| x == 0) {
                return (it, true);
            }

            // max_by_key віддає ОСТАННІЙ з-поміж рівних, тож нічию розв'язуємо
            // явно: Reverse(i) робить переможцем найменший індекс — як у Python.
            let (score, i) = (0..self.n)
                .map(|i| {
                    let score: u32 = self.bit_chk[self.bit_ptr[i]..self.bit_ptr[i + 1]]
                        .iter()
                        .map(|&j| s[j] as u32)
                        .sum();
                    (score, i)
                })
                .max_by_key(|&(score, i)| (score, Reverse(i)))
                .unwrap();

            if score == 0 {
                return (it, false); // звинуватити нікого — глухий кут
            }

            w[i] ^= 1;
            for &j in &self.bit_chk[self.bit_ptr[i]..self.bit_ptr[i + 1]] {
                s[j] ^= 1; // інкрементно
            }
        }

        (max_iter, s.iter().all(|&x| x == 0))
    }
}
