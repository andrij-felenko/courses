// 64-бітний результат тримаємо в BigInt.
function varintDecodeU64(buf) {
    let result = 0n;
    let shift = 0n;
    for (let i = 0; i < buf.length; i++) {
        const b = buf[i];
        result |= BigInt(b & 0x7f) << shift;
        if ((b & 0x80) === 0) {
            return { value: result, bytes: i + 1 };
        }
        shift += 7n;
        if (shift >= 64n) return null;
    }
    return null;
}
