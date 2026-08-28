#include <ctype.h>

const DiophExpr* dioph_parse_sexpr(DiophContext* ctx, const char** text) {
    while (**text && isspace((unsigned char)**text)) (*text)++;
    if (!**text) return NULL;

    if (**text == '(') {
        (*text)++; // Пропускаємо '('
        while (**text && isspace((unsigned char)**text)) (*text)++;
        char op[16] = {0};
        int i = 0;
        while (**text && !isspace((unsigned char)**text) && **text != ')' && i < 15) {
            op[i++] = *(*text)++;
        }

        const DiophExpr* res = NULL;
        if (strcmp(op, "add") == 0) {
            const DiophExpr* l = dioph_parse_sexpr(ctx, text);
            const DiophExpr* r = dioph_parse_sexpr(ctx, text);
            res = dioph_add(ctx, l, r);
        } else if (strcmp(op, "mul") == 0) {
            const DiophExpr* l = dioph_parse_sexpr(ctx, text);
            const DiophExpr* r = dioph_parse_sexpr(ctx, text);
            res = dioph_mul(ctx, l, r);
        } else if (strcmp(op, "const") == 0) {
            int64_t val = strtoll(*text, (char**)text, 10);
            res = dioph_const(ctx, val);
        }

        while (**text && isspace((unsigned char)**text)) (*text)++;
        if (**text == ')') (*text)++;
        return res;
    } else {
        // Змінна
        char var_name[32] = {0};
        int i = 0;
        while (**text && !isspace((unsigned char)**text) && **text != ')' && i < 31) {
            var_name[i++] = *(*text)++;
        }
        return dioph_var(ctx, var_name);
    }
}
