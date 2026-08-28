    /* 4. Завантажити крихітного 16-бітного гостя в цю пам'ять. */
    const unsigned char guest[] = {
        0xba, 0xf8, 0x03,   /* mov dx, 0x3f8   ; dx = порт COM1 */
        0x00, 0xd8,         /* add al, bl      ; al = al + bl */
        0x04, '0',          /* add al, '0'     ; число → цифра ASCII */
        0xee,               /* out dx, al      ; байт al у порт dx */
        0xb0, '\n',         /* mov al, 0x0a */
        0xee,               /* out dx, al */
        0xf4,               /* hlt             ; спинися */
    };
    memcpy(mem, guest, sizeof(guest));
