#include <stdint.h>
#include <stdio.h>

enum msg_kind {
    MSG_INT,        // у payload чинне поле i
    MSG_FLOAT,      // чинне f
    MSG_CMD         // чинне cmd
};

typedef struct {
    enum msg_kind kind;      // ТЕГ: який член об'єднання зараз чинний
    union {
        int32_t i;
        float   f;
        uint8_t cmd;
    } payload;               // самі дані — на спільній пам'яті
} Message;

void print_msg(const Message *m) {
    switch (m->kind) {                     // тег вирішує, як читати payload
        case MSG_INT:
            printf("ціле: %d\n", m->payload.i);
            break;
        case MSG_FLOAT:
            printf("дійсне: %.2f\n", m->payload.f);
            break;
        case MSG_CMD:
            printf("команда: %u\n", m->payload.cmd);
            break;
    }
}

int main(void) {
    Message a = { .kind = MSG_FLOAT, .payload = { .f = 23.5f } };
    Message b = { .kind = MSG_INT,   .payload = { .i = -7 } };

    print_msg(&a);    // дійсне: 23.50
    print_msg(&b);    // ціле: -7
    return 0;
}
