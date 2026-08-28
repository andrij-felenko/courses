/* Інтерпретатор байткоду правил плюралізації CLDR на C99 */
emb_plural_category_t emb_eval_plural_bytecode(const uint8_t *bytecode, int32_t n) {
    if (!bytecode) return EMB_PLURAL_OTHER;
    
    int32_t stack[8];
    int sp = 0;
    int32_t abs_n = n < 0 ? -n : n;
    const uint8_t *ip = bytecode;
    
    while (*ip != 0x00) {
        uint8_t op = *ip++;
        switch (op) {
            case 0x01: stack[sp++] = abs_n; break;
            case 0x04: stack[sp++] = *ip++; break;
            case 0x05: {
                int32_t b = stack[--sp];
                int32_t a = stack[--sp];
                stack[sp++] = (b != 0) ? (a % b) : 0;
                break;
            }
            case 0x06: {
                int32_t b = stack[--sp];
                int32_t a = stack[--sp];
                stack[sp++] = (a == b) ? 1 : 0;
                break;
            }
            case 0x07: {
                int32_t b = stack[--sp];
                int32_t a = stack[--sp];
                stack[sp++] = (a != b) ? 1 : 0;
                break;
            }
            case 0x08: {
                uint8_t low = *ip++;
                uint8_t high = *ip++;
                int32_t val = stack[--sp];
                stack[sp++] = (val >= low && val <= high) ? 1 : 0;
                break;
            }
            case 0x09: {
                int32_t b = stack[--sp];
                int32_t a = stack[--sp];
                stack[sp++] = (a && b) ? 1 : 0;
                break;
            }
            case 0x0B: {
                uint8_t target = *ip++;
                if (!stack[--sp]) ip = bytecode + target;
                break;
            }
            case 0x0C: return (emb_plural_category_t)(*ip);
            default: return EMB_PLURAL_OTHER;
        }
    }
    return EMB_PLURAL_OTHER;
}
