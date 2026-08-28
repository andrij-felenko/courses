// Закодувати value у varint, повернути Uint8Array (значення до 2^32-1).
function varintEncodeU32(value) {
    const out = [];
    // Поки лишаються біти ПОНАД молодші сім — ставимо прапорець «далі ще є».
    while (value >= 0x80) {              // >= 0x80 означає: є що кодувати після цих 7 бітів
        out.push((value & 0x7f) | 0x80); // молодші 7 бітів + старший біт = 1
        value = Math.floor(value / 128); // з'їли сім бітів (>>>7 псує 32-й біт)
    }
    out.push(value);                     // останній байт: старший біт = 0 (бо value < 0x80)
    return Uint8Array.from(out);
}
