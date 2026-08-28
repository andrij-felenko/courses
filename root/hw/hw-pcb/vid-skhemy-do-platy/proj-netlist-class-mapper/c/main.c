#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_NAME_LEN 128
#define MAX_PINS_PER_NET 128
#define MAX_NETS 1024
#define MAX_RULES 64

typedef enum {
    CLASS_DEFAULT = 0,
    CLASS_POWER,
    CLASS_HIGH_SPEED,
    CLASS_ANALOG,
    CLASS_RF
} NetClassId;

const char* netclass_to_str(NetClassId id) {
    switch (id) {
        case CLASS_POWER:      return "Power";
        case CLASS_HIGH_SPEED: return "HighSpeed";
        case CLASS_ANALOG:     return "Analog";
        case CLASS_RF:         return "RF";
        default:               return "Default";
    }
}

typedef struct {
    char refdes[MAX_NAME_LEN];
    char pin_num[MAX_NAME_LEN];
    char pin_type[MAX_NAME_LEN];
} PinConnection;

typedef struct {
    char name[MAX_NAME_LEN];
    int code;
    PinConnection pins[MAX_PINS_PER_NET];
    size_t pin_count;
    NetClassId assigned_class;
    double track_width_mm;
    double clearance_mm;
    double via_drill_mm;
    double via_pad_mm;
} NetDeclaration;

typedef struct {
    char pattern[MAX_NAME_LEN];
    NetClassId target_class;
    int priority;
    double track_width_mm;
    double clearance_mm;
    double via_drill_mm;
    double via_pad_mm;
} MappingRule;

typedef struct {
    NetDeclaration nets[MAX_NETS];
    size_t net_count;
    MappingRule rules[MAX_RULES];
    size_t rule_count;
} NetlistContext;

void context_init(NetlistContext* ctx) {
    if (!ctx) return;
    ctx->net_count = 0;
    ctx->rule_count = 0;
}

int add_rule(NetlistContext* ctx, const char* pattern, NetClassId cls, int priority,
             double width, double clearance, double via_drill, double via_pad) {
    if (!ctx || ctx->rule_count >= MAX_RULES) return 0;
    MappingRule* r = &ctx->rules[ctx->rule_count++];
    strncpy(r->pattern, pattern, MAX_NAME_LEN - 1);
    r->pattern[MAX_NAME_LEN - 1] = '\0';
    r->target_class = cls;
    r->priority = priority;
    r->track_width_mm = width;
    r->clearance_mm = clearance;
    r->via_drill_mm = via_drill;
    r->via_pad_mm = via_pad;
    return 1;
}

static int pattern_matches(const char* pattern, const char* text) {
    if (strcmp(pattern, "*") == 0) return 1;
    size_t plen = strlen(pattern);
    size_t tlen = strlen(text);

    // Префіксний шаблон: "USB_*"
    if (pattern[plen - 1] == '*') {
        if (tlen < plen - 1) return 0;
        return strncmp(pattern, text, plen - 1) == 0;
    }
    // Суфіксний шаблон: "*_GND"
    if (pattern[0] == '*') {
        if (tlen < plen - 1) return 0;
        return strcmp(pattern + 1, text + (tlen - (plen - 1))) == 0;
    }
    // Точний збіг
    return strcmp(pattern, text) == 0;
}

void apply_classification(NetlistContext* ctx) {
    if (!ctx) return;

    for (size_t i = 0; i < ctx->net_count; ++i) {
        NetDeclaration* net = &ctx->nets[i];
        net->assigned_class = CLASS_DEFAULT;
        net->track_width_mm = 0.20;
        net->clearance_mm = 0.20;
        net->via_drill_mm = 0.30;
        net->via_pad_mm = 0.60;

        int highest_priority = -1;

        for (size_t r = 0; r < ctx->rule_count; ++r) {
            MappingRule* rule = &ctx->rules[r];
            if (pattern_matches(rule->pattern, net->name)) {
                if (rule->priority > highest_priority) {
                    highest_priority = rule->priority;
                    net->assigned_class = rule->target_class;
                    net->track_width_mm = rule->track_width_mm;
                    net->clearance_mm = rule->clearance_mm;
                    net->via_drill_mm = rule->via_drill_mm;
                    net->via_pad_mm = rule->via_pad_mm;
                }
            }
        }
    }
}

static const char* skip_whitespace_and_comments(const char* p) {
    while (*p) {
        if (isspace((unsigned char)*p) || *p == '\r' || *p == '\n') {
            p++;
        } else if (*p == ';') { // Коментар у S-expr
            while (*p && *p != '\n') p++;
        } else {
            break;
        }
    }
    return p;
}

static const char* extract_token(const char* p, char* dest, size_t max_dest) {
    p = skip_whitespace_and_comments(p);
    if (!*p) return NULL;

    size_t idx = 0;
    if (*p == '"') {
        p++;
        while (*p && *p != '"' && idx < max_dest - 1) {
            dest[idx++] = *p++;
        }
        if (*p == '"') p++;
    } else {
        while (*p && !isspace((unsigned char)*p) && *p != '(' && *p != ')' && idx < max_dest - 1) {
            dest[idx++] = *p++;
        }
    }
    dest[idx] = '\0';
    return p;
}

int parse_s_expression_netlist(NetlistContext* ctx, const char* buffer) {
    if (!ctx || !buffer) return 0;
    const char* p = buffer;
    char token[MAX_NAME_LEN];

    while (*p) {
        p = skip_whitespace_and_comments(p);
        if (*p == '(') {
            p++;
            p = extract_token(p, token, MAX_NAME_LEN);
            if (!p) break;

            if (strcmp(token, "net") == 0) {
                if (ctx->net_count >= MAX_NETS) break;
                NetDeclaration* net = &ctx->nets[ctx->net_count];
                net->pin_count = 0;
                net->name[0] = '\0';
                net->code = (int)ctx->net_count + 1;

                while (*p && *p != ')') {
                    p = skip_whitespace_and_comments(p);
                    if (*p == '(') {
                        p++;
                        char sub_tag[MAX_NAME_LEN];
                        p = extract_token(p, sub_tag, MAX_NAME_LEN);
                        if (!p) break;

                        if (strcmp(sub_tag, "name") == 0) {
                            p = extract_token(p, net->name, MAX_NAME_LEN);
                            while (*p && *p != ')') p++;
                            if (*p == ')') p++;
                        } else if (strcmp(sub_tag, "node") == 0) {
                            if (net->pin_count < MAX_PINS_PER_NET) {
                                PinConnection* pin = &net->pins[net->pin_count];
                                pin->refdes[0] = '\0';
                                pin->pin_num[0] = '\0';
                                pin->pin_type[0] = '\0';

                                while (*p && *p != ')') {
                                    p = skip_whitespace_and_comments(p);
                                    if (*p == '(') {
                                        p++;
                                        char attr_name[MAX_NAME_LEN];
                                        p = extract_token(p, attr_name, MAX_NAME_LEN);
                                        if (!p) break;
                                        if (strcmp(attr_name, "ref") == 0) {
                                            p = extract_token(p, pin->refdes, MAX_NAME_LEN);
                                        } else if (strcmp(attr_name, "pin") == 0) {
                                            p = extract_token(p, pin->pin_num, MAX_NAME_LEN);
                                        } else if (strcmp(attr_name, "pintype") == 0) {
                                            p = extract_token(p, pin->pin_type, MAX_NAME_LEN);
                                        }
                                        while (*p && *p != ')') p++;
                                        if (*p == ')') p++;
                                    } else {
                                        p++;
                                    }
                                }
                                net->pin_count++;
                            }
                            if (*p == ')') p++;
                        } else {
                            while (*p && *p != ')') p++;
                            if (*p == ')') p++;
                        }
                    } else if (*p == ')') {
                        p++;
                        break;
                    } else {
                        p++;
                    }
                }
                if (net->name[0] != '\0') {
                    ctx->net_count++;
                }
            }
        } else {
            p++;
        }
    }
    return (int)ctx->net_count;
}

void print_netlist_audit_report(const NetlistContext* ctx) {
    if (!ctx) return;
    printf("\n========================================================================================\n");
    printf("                  PCB NETLIST CLASSIFICATION & DESIGN RULE REPORT (C99)\n");
    printf("========================================================================================\n");
    printf("%-24s | %-12s | %-8s | %-10s | %-12s | %-6s\n",
           "Net Identifier", "Class", "Width", "Clearance", "Via (D/P)", "Nodes");
    printf("----------------------------------------------------------------------------------------\n");

    for (size_t i = 0; i < ctx->net_count; ++i) {
        const NetDeclaration* n = &ctx->nets[i];
        char via_str[32];
        snprintf(via_str, sizeof(via_str), "%.2f/%.2f", n->via_drill_mm, n->via_pad_mm);

        printf("%-24s | %-12s | %5.2f mm | %6.2f mm | %-12s | %4zu\n",
               n->name, netclass_to_str(n->assigned_class),
               n->track_width_mm, n->clearance_mm, via_str, n->pin_count);
    }
    printf("========================================================================================\n");
    printf("Total electrical nets parsed: %zu\n\n", ctx->net_count);
}
