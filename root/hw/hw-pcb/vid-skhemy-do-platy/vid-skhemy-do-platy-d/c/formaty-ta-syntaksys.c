#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_IDENT_LEN 64

typedef struct PinNode {
    char refdes[MAX_IDENT_LEN];
    char pin_number[MAX_IDENT_LEN];
    char pin_type[MAX_IDENT_LEN];
    struct PinNode* next;
} PinNode;

typedef struct NetEntry {
    char name[MAX_IDENT_LEN];
    int code;
    size_t pin_count;
    PinNode* pins;
    struct NetEntry* next;
} NetEntry;

typedef struct NetlistGraph {
    NetEntry* head_net;
    size_t total_nets;
} NetlistGraph;

NetlistGraph* netlist_graph_create(void) {
    NetlistGraph* g = (NetlistGraph*)malloc(sizeof(NetlistGraph));
    if (!g) return NULL;
    g->head_net = NULL;
    g->total_nets = 0;
    return g;
}

int netlist_graph_add_pin(NetlistGraph* g, const char* net_name,
                          const char* refdes, const char* pin, const char* pintype) {
    if (!g || !net_name || !refdes || !pin) return 0;

    NetEntry* curr = g->head_net;
    while (curr) {
        if (strcmp(curr->name, net_name) == 0) break;
        curr = curr->next;
    }

    if (!curr) {
        curr = (NetEntry*)malloc(sizeof(NetEntry));
        if (!curr) return 0;
        strncpy(curr->name, net_name, MAX_IDENT_LEN - 1);
        curr->name[MAX_IDENT_LEN - 1] = '\0';
        curr->code = (int)(g->total_nets + 1);
        curr->pin_count = 0;
        curr->pins = NULL;
        curr->next = g->head_net;
        g->head_net = curr;
        g->total_nets++;
    }

    PinNode* p = (PinNode*)malloc(sizeof(PinNode));
    if (!p) return 0;
    strncpy(p->refdes, refdes, MAX_IDENT_LEN - 1);
    p->refdes[MAX_IDENT_LEN - 1] = '\0';
    strncpy(p->pin_number, pin, MAX_IDENT_LEN - 1);
    p->pin_number[MAX_IDENT_LEN - 1] = '\0';
    strncpy(p->pin_type, pintype ? pintype : "passive", MAX_IDENT_LEN - 1);
    p->pin_type[MAX_IDENT_LEN - 1] = '\0';

    p->next = curr->pins;
    curr->pins = p;
    curr->pin_count++;
    return 1;
}

void netlist_graph_destroy(NetlistGraph* g) {
    if (!g) return;
    NetEntry* n = g->head_net;
    while (n) {
        NetEntry* next_n = n->next;
        PinNode* p = n->pins;
        while (p) {
            PinNode* next_p = p->next;
            free(p);
            p = next_p;
        }
        free(n);
        n = next_n;
    }
    free(g);
}
