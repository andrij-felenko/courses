#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <nftables/libnftables.h>

int main(void) {
    struct nft_ctx *ctx = nft_ctx_new(NFT_CTX_DEFAULT);
    if (!ctx) {
        fprintf(stderr, "Помилка: не вдалося створити контекст nftables\n");
        return EXIT_FAILURE;
    }

    /* Увімкнення перехоплення стандартного виводу у буфер */
    nft_ctx_buffer_output(ctx);

    /* Команди створення таблиці, ланцюжка та базових правил */
    const char *commands =
        "flush ruleset\n"
        "add table inet filter_demo\n"
        "add chain inet filter_demo input_demo { type filter hook input priority 0; policy drop; }\n"
        "add rule inet filter_demo input_demo ct state invalid drop\n"
        "add rule inet filter_demo input_demo ct state established,related accept\n"
        "add rule inet filter_demo input_demo iifname \"lo\" accept\n"
        "add rule inet filter_demo input_demo tcp dport 22 accept\n";

    printf("=== Завантаження правил nftables ===\n");
    int ret = nft_run_cmd_from_buffer(ctx, commands);
    if (ret != 0) {
        fprintf(stderr, "Помилка застосування правил nftables (код %d)\n", ret);
        nft_ctx_free(ctx);
        return EXIT_FAILURE;
    }
    printf("Правила успішно застосовано.\n\n");

    /* Запит виводу поточного правилсету у текстовому вигляді */
    const char *list_cmd = "list ruleset\n";
    ret = nft_run_cmd_from_buffer(ctx, list_cmd);
    if (ret == 0) {
        const char *output = nft_ctx_get_output_buffer(ctx);
        if (output) {
            printf("=== Поточний Ruleset ядра ===\n%s", output);
        }
    } else {
        fprintf(stderr, "Помилка читання ruleset\n");
    }

    nft_ctx_free(ctx);
    return EXIT_SUCCESS;
}
