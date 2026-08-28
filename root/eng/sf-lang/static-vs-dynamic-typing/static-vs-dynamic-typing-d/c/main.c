#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Універсальне динамічне значення у C через дискриміноване об'єднання */
typedef enum { TYPE_INT, TYPE_STRING, TYPE_INVALID } DataType;

typedef struct {
    DataType type;
    union {
        int int_val;
        char *str_val;
    } as;
} DynamicBox;

DynamicBox make_int(int v) {
    DynamicBox b;
    b.type = TYPE_INT;
    b.as.int_val = v;
    return b;
}

DynamicBox make_str(const char *s) {
    DynamicBox b;
    b.type = TYPE_STRING;
    b.as.str_val = strdup(s);
    return b;
}

void print_box(const DynamicBox *b) {
    if (b->type == TYPE_INT) {
        printf("Int: %d\n", b->as.int_val);
    } else if (b->type == TYPE_STRING) {
        printf("String: %s\n", b->as.str_val);
    }
}

void free_box(DynamicBox *b) {
    if (b->type == TYPE_STRING && b->as.str_val) {
        free(b->as.str_val);
        b->as.str_val = NULL;
    }
}

int main(void) {
    DynamicBox b1 = make_int(100);
    DynamicBox b2 = make_str("Статична мова з динамічним контейнером");

    print_box(&b1);
    print_box(&b2);

    free_box(&b1);
    free_box(&b2);
    return 0;
}
