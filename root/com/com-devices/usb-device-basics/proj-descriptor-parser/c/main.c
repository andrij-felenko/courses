#include <stdint.h>
#include <stdio.h>

/* --- типи дескрипторів (поле bDescriptorType) --- */
enum {
    DESC_CONFIGURATION = 0x02,
    DESC_INTERFACE     = 0x04,
    DESC_ENDPOINT      = 0x05,
};

/* --- зібране дерево: фіксовані масиви, без malloc (як на МК) --- */
#define MAX_INTERFACES 8
#define MAX_ENDPOINTS  8

typedef struct {
    uint8_t  address;      /* bEndpointAddress: біт 7 — напрям, біти 3..0 — номер */
    uint8_t  attributes;   /* bmAttributes: біти 1..0 — тип передачі */
    uint16_t max_packet;   /* wMaxPacketSize */
    uint8_t  interval;     /* bInterval */
} endpoint_t;

typedef struct {
    uint8_t    number;       /* bInterfaceNumber */
    uint8_t    class_code;    /* bInterfaceClass */
    uint8_t    declared_eps;  /* bNumEndpoints — скільки точок ОБІЦЯНО */
    endpoint_t endpoints[MAX_ENDPOINTS];
    uint8_t    ep_count;      /* скільки реально нанизали */
} interface_t;

typedef struct {
    uint16_t    total_length;   /* wTotalLength із дескриптора конфігурації */
    uint8_t     num_interfaces; /* bNumInterfaces */
    interface_t interfaces[MAX_INTERFACES];
    uint8_t     if_count;
} config_tree_t;

/* 16-бітне little-endian поле, зібране з двох байтів.
   НЕ розіменовуємо (uint16_t*)(buf+off): поле лежить на довільному,
   часто непарному зсуві, а Cortex-M0 на невирівняному доступі падає. */
static uint16_t le16(const uint8_t *p) {
    return (uint16_t)(p[0] | (p[1] << 8));
}

/* Розбір буфера конфігурації у дерево.
   Повертає 0 при успіху, -1 при пошкодженому буфері. */
int parse_config(const uint8_t *buf, uint16_t len, config_tree_t *tree) {
    tree->if_count = 0;
    tree->total_length = 0;
    tree->num_interfaces = 0;
    interface_t *cur = NULL;    /* інтерфейс, на який зараз нанизуємо точки */

    uint16_t off = 0;
    while (off + 2u <= len) {                       /* треба хоча б bLength + bDescriptorType */
        uint8_t b_len  = buf[off];
        uint8_t b_type = buf[off + 1];

        if (b_len == 0) return -1;                  /* нульова довжина → вічний цикл */
        if ((uint32_t)off + b_len > len) return -1; /* дескриптор вилазить за буфер */

        switch (b_type) {
        case DESC_CONFIGURATION:
            if (b_len < 9) return -1;
            tree->total_length   = le16(buf + off + 2);
            tree->num_interfaces = buf[off + 4];
            break;

        case DESC_INTERFACE:
            if (b_len < 9) return -1;
            if (tree->if_count >= MAX_INTERFACES) return -1;
            cur = &tree->interfaces[tree->if_count++];
            cur->number       = buf[off + 2];
            cur->class_code   = buf[off + 5];
            cur->declared_eps = buf[off + 4];
            cur->ep_count     = 0;
            break;

        case DESC_ENDPOINT: {
            if (b_len < 7) return -1;
            if (cur == NULL) return -1;             /* точка раніше за свій інтерфейс */
            if (cur->ep_count >= MAX_ENDPOINTS) return -1;
            endpoint_t *ep = &cur->endpoints[cur->ep_count++];
            ep->address    = buf[off + 2];
            ep->attributes = buf[off + 3];
            ep->max_packet = le16(buf + off + 4);
            ep->interval   = buf[off + 6];
            break;
        }

        default:
            /* класоспецифічний (0x24/0x25) або невідомий — просто крокуємо далі */
            break;
        }

        off += b_len;   /* КЛЮЧОВИЙ КРОК: рухаємось на довжину поточного дескриптора */
    }
    return 0;
}

/* --- друк зібраного дерева --- */
static const char *xfer(uint8_t attr) {
    switch (attr & 0x03u) {
    case 0:  return "контрольна";
    case 1:  return "ізохронна";
    case 2:  return "масова";
    default: return "переривна";
    }
}

static void dump_tree(const config_tree_t *t) {
    printf("Конфігурація: wTotalLength=%u, інтерфейсів=%u\n",
           t->total_length, t->num_interfaces);
    for (uint8_t i = 0; i < t->if_count; i++) {
        const interface_t *f = &t->interfaces[i];
        printf("  Інтерфейс %u  клас 0x%02X  точок: %u (обіцяно %u)\n",
               f->number, f->class_code, f->ep_count, f->declared_eps);
        for (uint8_t j = 0; j < f->ep_count; j++) {
            const endpoint_t *e = &f->endpoints[j];
            printf("    Точка 0x%02X  %-3s  %s  wMaxPacketSize=%u\n",
                   e->address,
                   (e->address & 0x80u) ? "IN" : "OUT",
                   xfer(e->attributes),
                   e->max_packet);
        }
    }
}

/* Сирий дамп конфігурації віртуального COM-порту (CDC-ACM), 67 байтів. */
static const uint8_t raw[] = {
    /* Конфігурація (9): wTotalLength=0x0043=67, 2 інтерфейси, 100 мА */
    0x09,0x02, 0x43,0x00, 0x02, 0x01, 0x00, 0x80, 0x32,
    /* Інтерфейс 0 (9): CDC-Communications, клас 0x02 */
    0x09,0x04, 0x00, 0x00, 0x01, 0x02, 0x02, 0x01, 0x00,
    /* 4 класоспецифічні дескриптори CDC (тип CS_INTERFACE = 0x24) */
    0x05,0x24, 0x00, 0x10,0x01,          /* Header */
    0x05,0x24, 0x01, 0x00, 0x01,         /* Call Management */
    0x04,0x24, 0x02, 0x02,               /* Abstract Control Management */
    0x05,0x24, 0x06, 0x00, 0x01,         /* Union */
    /* Точка 0x81 (7): переривна IN, wMaxPacketSize=8 */
    0x07,0x05, 0x81, 0x03, 0x08,0x00, 0xFF,
    /* Інтерфейс 1 (9): CDC-Data, клас 0x0A */
    0x09,0x04, 0x01, 0x00, 0x02, 0x0A, 0x00, 0x00, 0x00,
    /* Точка 0x02 (7): масова OUT, wMaxPacketSize=64 */
    0x07,0x05, 0x02, 0x02, 0x40,0x00, 0x00,
    /* Точка 0x82 (7): масова IN, wMaxPacketSize=64 */
    0x07,0x05, 0x82, 0x02, 0x40,0x00, 0x00,
};

int main(void) {
    config_tree_t tree;
    if (parse_config(raw, (uint16_t)sizeof raw, &tree) != 0) {
        printf("пошкоджений дескриптор\n");
        return 1;
    }
    dump_tree(&tree);
    return 0;
}
