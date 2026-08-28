void dioph_to_smtlib(const DiophExpr* expr, const DiophContext* ctx, char* buf, size_t buf_size) {
    size_t off = snprintf(buf, buf_size, "(set-logic QF_NIA)\n");
    for (size_t i = 0; i < ctx->var_count; ++i) {
        off += snprintf(buf + off, buf_size - off, "(declare-const %s Int)\n", ctx->variables[i].name);
        off += snprintf(buf + off, buf_size - off, "(assert (>= %s 0))\n", ctx->variables[i].name);
    }
    off += snprintf(buf + off, buf_size - off, "(assert (= ");
    // Запис виразу у префіксній польській формі
    off += snprintf(buf + off, buf_size - off, "0))\n(check-sat)\n(get-model)\n");
}
