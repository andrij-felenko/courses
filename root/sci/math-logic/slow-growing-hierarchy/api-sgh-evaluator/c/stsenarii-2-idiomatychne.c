#include "sgh_engine.h"
#include <stdio.h>

void run_c_parser_example(void) {
    OrdinalNode *node = NULL;
    SghStatus st = sgh_parse_string("w^3 * 2 + w^2 * 5 + 7", &node);
    if (st != SGH_OK) {
        fprintf(stderr, "Помилка парсингу: %d\n", st);
        return;
    }
    uint64_t val = sgh_eval_homomorphism(node, 3);
    printf("Обчислено у C: %lu\n", (unsigned long)val);
    ord_free(node);
}
