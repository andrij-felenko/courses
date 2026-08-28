// Було: send_frame(payload, len, false, false, false);
// Стало: те саме тіло, але з підставленими прапорцями й викинутими
//        гілками, яких цей випадок не бере.
{
    uint8_t body[256];
    size_t  n = len;
    memcpy(body, payload, len);        // compress=false → просто копія
    // big_endian=false → перевороту нема

    uint8_t frame[300];
    size_t  f = 0;
    frame[f++] = 0xAA;
    frame[f++] = (uint8_t)n;
    memcpy(frame + f, body, n); f += n;
    // with_crc=false → CRC нема
    frame[f++] = 0x55;
    hw_tx(frame, f);
}
