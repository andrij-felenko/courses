// C99 / C11
struct __attribute__((packed)) DataFlash_FMT {
    uint8_t  head1;        // 0xA3
    uint8_t  head2;        // 0x95
    uint8_t  msg_type;     // 0x80 (FMT)
    uint8_t  type;         // Числовий ID типу, який описується цим FMT (1..255)
    uint8_t  length;       // Повна довжина майбутніх повідомлень цього типу в байтах
    char     name[4];      // 4-символьна назва структури ("ATT\0", "GPS\0", "IMU\0")
    char     format[16];   // Рядок символьних кодів типів полів ("Qffff", "Qcccc")
    char     columns[64];  // Назви полів через кому ("TimeUS,Roll,Pitch,Yaw,ErrRP")
};
