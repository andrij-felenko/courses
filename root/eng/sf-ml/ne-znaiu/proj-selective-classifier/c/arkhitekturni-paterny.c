typedef void (*decision_handler_fn)(const selective_output_t* result, void* user_ctx);

typedef struct {
    decision_handler_fn on_accepted;
    decision_handler_fn on_reject_ood;
    decision_handler_fn on_reject_ambiguous;
} decision_policy_table_t;

void dispatch_decision(const selective_output_t* res, const decision_policy_table_t* table, void* ctx) {
    if (!res || !table) return;
    switch (res->status) {
        case DECISION_STATUS_ACCEPTED:
            if (table->on_accepted) table->on_accepted(res, ctx);
            break;
        case DECISION_STATUS_REJECT_OOD:
            if (table->on_reject_ood) table->on_reject_ood(res, ctx);
            break;
        case DECISION_STATUS_REJECT_AMBIGUOUS:
            if (table->on_reject_ambiguous) table->on_reject_ambiguous(res, ctx);
            break;
    }
}
