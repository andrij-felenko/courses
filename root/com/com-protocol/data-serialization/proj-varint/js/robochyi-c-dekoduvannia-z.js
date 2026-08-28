// Повертає { value, bytes } при успіху, або null при помилці.
function varintDecodeU32(buf) {
    let result = 0;
    let shift = 0;
    for (let i = 0; i < buf.length; i++) {
        const b = buf[i];
        // Наростити результат: множимо на 2^shift (<< псує 32-й біт).
        result += (b & 0x7f) * 2 ** shift;
        if ((b & 0x80) === 0) {          // старший біт 0 → це останній байт числа
            return { value: result >>> 0, bytes: i + 1 }; // успіх
        }
        shift += 7;
        if (shift >= 32) return null;    // задовгий varint для 32 бітів → потік зіпсовано
    }
    return null;                         // прапорець ще «далі є», а буфер скінчився → обірвано
}
