/* Синтаксичний парсер та формувальник повідомлень зі статичним буфером на C99 */
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MSG_MAX_NODES 32
#define MSG_MAX_BRANCHES 8

typedef enum {
    MSG_ERR_OK = 0,
    MSG_ERR_SYNTAX,
    MSG_ERR_BUFFER_OVERFLOW,
    MSG_ERR_UNCLOSED_BRACE,
    MSG_ERR_MISSING_OTHER
} msg_err_t;

typedef enum {
    NODE_TEXT,
    NODE_ARG,
    NODE_HASH,
    NODE_CHOICE
} msg_node_type_t;

typedef struct {
    const char *ptr;
    size_t len;
} msg_str_t;

typedef struct {
    msg_str_t label;
    uint16_t child_start;
    uint16_t child_count;
} msg_branch_t;

typedef struct {
    msg_node_type_t type;
    msg_str_t str;
    bool is_plural;
    int32_t offset;
    uint16_t branch_start;
    uint16_t branch_count;
} msg_node_t;

typedef struct {
    const char *src;
    size_t len;
    size_t pos;
    msg_node_t nodes[MSG_MAX_NODES];
    size_t node_count;
    msg_branch_t branches[MSG_MAX_BRANCHES];
    size_t branch_count;
    msg_err_t err;
} msg_parser_t;

typedef struct {
    const char *name;
    const char *val_str;
    int32_t val_num;
    bool is_num;
} msg_arg_val_t;

typedef const char* (*msg_plural_fn)(int32_t num);

static bool str_eq(msg_str_t s, const char *lit) {
    size_t llen = strlen(lit);
    return s.len == llen && memcmp(s.ptr, lit, llen) == 0;
}

static void skip_ws(msg_parser_t *p) {
    while (p->pos < p->len && (p->src[p->pos] == ' ' || p->src[p->pos] == '\t' ||
                               p->src[p->pos] == '\n' || p->src[p->pos] == '\r')) {
        p->pos++;
    }
}

static msg_str_t parse_ident(msg_parser_t *p) {
    skip_ws(p);
    size_t start = p->pos;
    while (p->pos < p->len) {
        char c = p->src[p->pos];
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
            (c >= '0' && c <= '9') || c == '_' || c == '.' || c == '=') {
            p->pos++;
        } else {
            break;
        }
    }
    msg_str_t res = { .ptr = p->src + start, .len = p->pos - start };
    return res;
}

static uint16_t parse_message(msg_parser_t *p, bool in_branch, uint16_t *out_count);

static uint16_t parse_choice(msg_parser_t *p) {
    p->pos++; /* Пропуск '{' */
    msg_str_t arg_name = parse_ident(p);
    skip_ws(p);
    
    if (p->pos < p->len && p->src[p->pos] == '}') {
        p->pos++;
        if (p->node_count >= MSG_MAX_NODES) { p->err = MSG_ERR_BUFFER_OVERFLOW; return 0; }
        uint16_t idx = (uint16_t)p->node_count++;
        p->nodes[idx] = (msg_node_t){ .type = NODE_ARG, .str = arg_name };
        return idx;
    }
    
    if (p->pos >= p->len || p->src[p->pos] != ',') { p->err = MSG_ERR_SYNTAX; return 0; }
    p->pos++;
    
    msg_str_t kind = parse_ident(p);
    bool is_plural = str_eq(kind, "plural");
    if (!is_plural && !str_eq(kind, "select")) { p->err = MSG_ERR_SYNTAX; return 0; }
    
    skip_ws(p);
    if (p->pos >= p->len || p->src[p->pos] != ',') { p->err = MSG_ERR_SYNTAX; return 0; }
    p->pos++;
    
    if (p->node_count >= MSG_MAX_NODES) { p->err = MSG_ERR_BUFFER_OVERFLOW; return 0; }
    uint16_t choice_idx = (uint16_t)p->node_count++;
    uint16_t b_start = (uint16_t)p->branch_count;
    uint16_t b_count = 0;
    bool has_other = false;
    
    while (p->pos < p->len && p->src[p->pos] != '}') {
        skip_ws(p);
        if (p->pos < p->len && p->src[p->pos] == '}') break;
        
        msg_str_t lbl = parse_ident(p);
        if (lbl.len == 0) { p->err = MSG_ERR_SYNTAX; return choice_idx; }
        if (str_eq(lbl, "other")) has_other = true;
        
        skip_ws(p);
        if (p->pos >= p->len || p->src[p->pos] != '{') { p->err = MSG_ERR_SYNTAX; return choice_idx; }
        p->pos++;
        
        if (p->branch_count >= MSG_MAX_BRANCHES) { p->err = MSG_ERR_BUFFER_OVERFLOW; return choice_idx; }
        uint16_t b_idx = (uint16_t)p->branch_count++;
        b_count++;
        
        uint16_t child_cnt = 0;
        uint16_t child_st = parse_message(p, true, &child_cnt);
        p->branches[b_idx] = (msg_branch_t){ .label = lbl, .child_start = child_st, .child_count = child_cnt };
        
        if (p->pos >= p->len || p->src[p->pos] != '}') { p->err = MSG_ERR_UNCLOSED_BRACE; return choice_idx; }
        p->pos++;
    }
    
    if (p->pos >= p->len || p->src[p->pos] != '}') { p->err = MSG_ERR_UNCLOSED_BRACE; return choice_idx; }
    p->pos++;
    
    if (!has_other) { p->err = MSG_ERR_MISSING_OTHER; }
    
    p->nodes[choice_idx] = (msg_node_t){
        .type = NODE_CHOICE,
        .str = arg_name,
        .is_plural = is_plural,
        .offset = 0,
        .branch_start = b_start,
        .branch_count = b_count
    };
    return choice_idx;
}

static uint16_t parse_message(msg_parser_t *p, bool in_branch, uint16_t *out_count) {
    uint16_t start_idx = (uint16_t)p->node_count;
    uint16_t count = 0;
    size_t txt_start = p->pos;
    
    while (p->pos < p->len && p->err == MSG_ERR_OK) {
        char c = p->src[p->pos];
        if (in_branch && c == '}') break;
        
        if (c == '{' || (in_branch && c == '#')) {
            if (p->pos > txt_start) {
                if (p->node_count >= MSG_MAX_NODES) { p->err = MSG_ERR_BUFFER_OVERFLOW; break; }
                p->nodes[p->node_count++] = (msg_node_t){
                    .type = NODE_TEXT,
                    .str = { .ptr = p->src + txt_start, .len = p->pos - txt_start }
                };
                count++;
            }
            if (c == '#') {
                if (p->node_count >= MSG_MAX_NODES) { p->err = MSG_ERR_BUFFER_OVERFLOW; break; }
                p->nodes[p->node_count++] = (msg_node_t){ .type = NODE_HASH };
                count++;
                p->pos++;
                txt_start = p->pos;
            } else {
                parse_choice(p);
                count++;
                txt_start = p->pos;
            }
        } else {
            p->pos++;
        }
    }
    if (p->pos > txt_start && p->err == MSG_ERR_OK) {
        if (p->node_count < MSG_MAX_NODES) {
            p->nodes[p->node_count++] = (msg_node_t){
                .type = NODE_TEXT,
                .str = { .ptr = p->src + txt_start, .len = p->pos - txt_start }
            };
            count++;
        }
    }
    *out_count = count;
    return start_idx;
}

static size_t format_eval(const msg_parser_t *p, uint16_t start, uint16_t count,
                          const msg_arg_val_t *args, size_t argc, msg_plural_fn pl_fn,
                          int32_t active_num, char *out, size_t out_cap, size_t *out_pos) {
    for (uint16_t i = 0; i < count; ++i) {
        const msg_node_t *n = &p->nodes[start + i];
        if (n->type == NODE_TEXT) {
            size_t copy_len = n->str.len;
            if (*out_pos + copy_len >= out_cap) copy_len = out_cap > *out_pos ? out_cap - *out_pos - 1 : 0;
            memcpy(out + *out_pos, n->str.ptr, copy_len);
            *out_pos += copy_len;
        } else if (n->type == NODE_HASH) {
            char num_buf[16];
            int nlen = snprintf(num_buf, sizeof(num_buf), "%d", (int)active_num);
            size_t copy_len = (size_t)nlen;
            if (*out_pos + copy_len >= out_cap) copy_len = out_cap > *out_pos ? out_cap - *out_pos - 1 : 0;
            memcpy(out + *out_pos, num_buf, copy_len);
            *out_pos += copy_len;
        } else if (n->type == NODE_ARG) {
            for (size_t a = 0; a < argc; ++a) {
                if (str_eq(n->str, args[a].name)) {
                    const char *val = args[a].val_str;
                    char tmp[16];
                    if (args[a].is_num) {
                        snprintf(tmp, sizeof(tmp), "%d", (int)args[a].val_num);
                        val = tmp;
                    }
                    size_t vlen = strlen(val);
                    if (*out_pos + vlen >= out_cap) vlen = out_cap > *out_pos ? out_cap - *out_pos - 1 : 0;
                    memcpy(out + *out_pos, val, vlen);
                    *out_pos += vlen;
                    break;
                }
            }
        } else if (n->type == NODE_CHOICE) {
            const char *matched_lbl = "other";
            int32_t next_num = active_num;
            for (size_t a = 0; a < argc; ++a) {
                if (str_eq(n->str, args[a].name)) {
                    if (n->is_plural && args[a].is_num) {
                        next_num = args[a].val_num;
                        matched_lbl = pl_fn ? pl_fn(next_num) : "other";
                    } else if (!n->is_plural && !args[a].is_num) {
                        matched_lbl = args[a].val_str;
                    }
                    break;
                }
            }
            uint16_t sel_idx = 0;
            for (uint16_t b = 0; b < n->branch_count; ++b) {
                const msg_branch_t *br = &p->branches[n->branch_start + b];
                if (str_eq(br->label, matched_lbl)) { sel_idx = b; break; }
                if (str_eq(br->label, "other")) sel_idx = b;
            }
            const msg_branch_t *chosen = &p->branches[n->branch_start + sel_idx];
            format_eval(p, chosen->child_start, chosen->child_count, args, argc, pl_fn, next_num, out, out_cap, out_pos);
        }
    }
    if (*out_pos < out_cap) out[*out_pos] = '\0';
    return *out_pos;
}
