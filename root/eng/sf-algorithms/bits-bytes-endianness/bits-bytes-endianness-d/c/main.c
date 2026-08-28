// 4 байти прийшли в мережевому порядку: старший — першим
uint8_t buf[4] = { 0x12, 0x34, 0x56, 0x78 };

// (1) приведення через union — type punning:
union { uint8_t b[4]; uint32_t u; } v;
memcpy(v.b, buf, 4);
// v.u на BIG-endian   = 0x12345678  (як на дроті — пощастило)
// v.u на LITTLE-endian = 0x78563412  (байти «перевернуті» — баг)

// (2) приведення вказівника — те саме лихо + alignment + strict aliasing:
uint32_t x = *(uint32_t*)buf;   // НЕ робити так

// (3) явне складання зсувами — той самий результат СКРІЗЬ:
uint32_t ok = ((uint32_t)buf[0] << 24) | ((uint32_t)buf[1] << 16)
            | ((uint32_t)buf[2] <<  8) |  (uint32_t)buf[3];
// ok = 0x12345678 і на big-, і на little-endian
