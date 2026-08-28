#include <stdint.h>

typedef uintptr_t seL4_Word;
typedef seL4_Word seL4_CapRights_t;

#define seL4_CanRead        (1 << 0)  /* 0x1: читання даних або отримання IPC-повідомлень */
#define seL4_CanWrite       (1 << 1)  /* 0x2: запис даних або надсилання IPC-повідомлень */
#define seL4_CanGrant       (1 << 2)  /* 0x4: право передавати інші повноваження через IPC */
#define seL4_CanGrantReply  (1 << 3)  /* 0x8: право передавати одноразовий токен відповіді */
#define seL4_AllRights      (seL4_CanRead | seL4_CanWrite | seL4_CanGrant | seL4_CanGrantReply)
