parser_status parser_create(parser_ctx** out) noexcept {
    if (!out) return PARSER_E_ARG;
    *out = nullptr;
    try {
        *out = new parser_ctx{};    // кине конструктор cfg::Parser — рантайм
        return PARSER_OK;           // сам поверне щойно виділену пам'ять
    }
    catch (const std::bad_alloc&) { return PARSER_E_NO_MEMORY; }
    catch (...)                   { return PARSER_E_INTERNAL; }
}

parser_status parser_load(parser_ctx* ctx, const char* path) noexcept {
    return boundary(ctx, [&] {
        if (!path) throw std::invalid_argument("path == nullptr");
        ctx->impl.load(path);
    });
}

parser_status parser_get_int(parser_ctx* ctx, const char* key, long* out) noexcept {
    return boundary(ctx, [&] {
        if (!key || !out) throw std::invalid_argument("null argument");
        *out = ctx->impl.get_int(key);
    });
}

const char* parser_last_error(const parser_ctx* ctx) noexcept {
    return ctx ? ctx->message : "null context";
}
