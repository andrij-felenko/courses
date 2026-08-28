/* src/main.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "miniz.h"

int main(void) {
    const char *payload = "<telemetry version=\"1.0\"><sensor id=\"temp\" val=\"24.5\"/></telemetry>";
    size_t payload_len = strlen(payload);

    uLong bound_len = compressBound((uLong)payload_len);
    unsigned char *compressed = (unsigned char *)malloc(bound_len);
    if (!compressed) {
        fprintf(stderr, "Помилка виділення пам'яті під буфер стиснення\n");
        return 1;
    }

    uLong comp_len = bound_len;
    int status = compress(compressed, &comp_len, (const unsigned char *)payload, (uLong)payload_len);
    if (status != Z_OK) {
        fprintf(stderr, "Помилка стиснення даних: %d\n", status);
        free(compressed);
        return 1;
    }

    printf("Розмір початковий: %zu байтів, розмір стиснений: %lu байтів\n", payload_len, comp_len);
    free(compressed);
    return 0;
}
