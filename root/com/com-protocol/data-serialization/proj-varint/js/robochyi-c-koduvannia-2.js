// 64-бітні значення не влазять у Number — беремо BigInt.
function varintEncodeU64(value) {
    const out = [];
    while (value >= 0x80n) {
        out.push(Number((value & 0x7fn) | 0x80n));
        value >>= 7n;
    }
    out.push(Number(value));
    return Uint8Array.from(out);
}
