/* src/main.c */
#include <fastcodec/fastcodec.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    printf("FastCodec C client, version %s\n", FASTCODEC_VERSION_STRING);
    
    fastcodec_config_t config;
    fastcodec_get_default_config(&config);
    
    fastcodec_ctx_t* ctx = fastcodec_create_context(&config);
    if (!ctx) {
        fprintf(stderr, "Помилка ініціалізації контексту стиснення\n");
        return EXIT_FAILURE;
    }
    
    printf("Контекст стиснення успішно створено.\n");
    fastcodec_free_context(ctx);
    return EXIT_SUCCESS;
}
