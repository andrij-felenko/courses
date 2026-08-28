/* Мова C: розмічене об'єднання з небезпечним доступом до бітів */
#include <stdio.h>
#include <stdlib.h>

enum ValueType { TYPE_INT, TYPE_DOUBLE, TYPE_STRING };

struct CTaggedUnion {
    enum ValueType type;
    union {
        int i_val;
        double d_val;
        char* s_val;
    } data;
};

void print_c_value(const struct CTaggedUnion* val) {
    /* Небезпека: компілятор не перевіряє відповідність type і поля data */
    if (val->type == TYPE_INT) {
        printf("Int: %d\n", val->data.i_val);
    } else if (val->type == TYPE_DOUBLE) {
        printf("Double: %f\n", val->data.d_val);
    } else if (val->type == TYPE_STRING) {
        printf("String: %s\n", val->data.s_val);
    }
}
