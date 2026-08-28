#include <stdint.h>

struct rpmlead {
    unsigned char magic[4];      /* 0xED, 0xAB, 0xEE, 0xDB */
    unsigned char major;         /* Версія формату (наразі 3 або 4) */
    unsigned char minor;         /* Підверсія формату */
    uint16_t type;               /* 0 = Binary, 1 = Source */
    uint16_t archtag;            /* Ідентифікатор архітектури (1 = x86) */
    char name[66];               /* Назва пакунка (доповнена нульовими байтами) */
    uint16_t osnum;              /* Ідентифікатор ОС (1 = Linux) */
    uint16_t signature_type;     /* Тип заголовку підпису (зазвичай 5 = Header-style) */
    char reserved[16];           /* Зарезервоване поле (нульові байти) */
};
