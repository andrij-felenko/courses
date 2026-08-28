enum : uint8_t  { MSG_REQUEST = 0, MSG_REPLY = 1 };
enum : uint32_t { REPLY_OK = 0, REPLY_USER_EX = 1, REPLY_SYS_EX = 2 };

void put_header(Out& o, uint8_t type) {
    o.raw("MORB", 4);                       // 0…3   мітка: наш це потік чи ні
    o.u8(1); o.u8(0);                       // 4…5   версія
    o.u8(host_is_little() ? 1 : 0);         // 6     біт 0 — порядок байтів
    o.u8(type);                             // 7     запит чи відповідь
    o.u32(0);                               // 8…11  розмір тіла — залатаємо потім
}

void finish(Out& o) {
    // розмір відомий лише тоді, коли тіло вже написане
    o.patch_u32(8, static_cast<uint32_t>(o.bytes().size() - 12));
}
