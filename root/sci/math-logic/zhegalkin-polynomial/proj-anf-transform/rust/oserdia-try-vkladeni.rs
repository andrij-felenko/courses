// t — зріз із 2^n значень 0/1; згортається на місці в коефіцієнти
fn anf_transform(t: &mut [u8]) {
    let mut step = 1;
    while step < t.len() {                  // по одному біту-змінній за раз
        for block in t.chunks_mut(step << 1) {          // блок = дві сусідні половини
            let (lo, hi) = block.split_at_mut(step);
            for (a, b) in lo.iter().zip(hi.iter_mut()) {
                *b ^= *a;                   // половину-з-одиницею ⊕ половина-з-нулем
            }
        }
        step <<= 1;
    }
}
