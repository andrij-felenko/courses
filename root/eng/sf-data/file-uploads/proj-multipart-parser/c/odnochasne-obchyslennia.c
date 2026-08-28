/* Ініціалізація SHA-256 у колбеку початку частини */
SHA256_Init(&user_ctx->sha256_ctx);

/* У колбеку on_part_data байти одночасно летять у сокет/диск та в хеш-функцію */
void on_part_data_handler(const unsigned char *data, size_t len, void *user_data) {
    upload_context_t *ctx = (upload_context_t *)user_data;
    write(ctx->out_fd, data, len);              /* запис на диск */
    SHA256_Update(&ctx->sha256_ctx, data, len); /* оновлення хешу в L1-кеші */
}

/* У колбеку on_part_end фіналізується результат */
SHA256_Final(ctx->final_sha256_digest, &ctx->sha256_ctx);
