// wire types
const WT_VARINT = 0, WT_I64 = 1, WT_LEN = 2, WT_I32 = 5;

// Записати тег поля (номер + тип); повертає Uint8Array.
function tagEncode(fieldNum, wireType) {
    const tag = (fieldNum << 3) | (wireType & 0x07);
    return varintEncodeU32(tag >>> 0);             // тег — теж varint
}

// Розібрати тег: { fieldNum, wireType, bytes } або null при помилці.
function tagDecode(buf) {
    const r = varintDecodeU32(buf);
    if (r === null) return null;                   // обірваний/зіпсований тег
    return {
        wireType: r.value & 0x07,                  // три молодші біти — тип
        fieldNum: r.value >>> 3,                   // решта — номер поля
        bytes: r.bytes,
    };
}
