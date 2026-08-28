typedef struct {
    size_t size;
    fenwick_tree_t* t1;
    fenwick_tree_t* t2;
} fenwick_range_range_t;

fenwick_range_range_t* fenwick_rr_create(size_t size) {
    fenwick_range_range_t* frr = (fenwick_range_range_t*)malloc(sizeof(fenwick_range_range_t));
    if (!frr) return NULL;
    frr->size = size;
    frr->t1 = fenwick_create(size);
    frr->t2 = fenwick_create(size);
    if (!frr->t1 || !frr->t2) {
        fenwick_destroy(frr->t1);
        fenwick_destroy(frr->t2);
        free(frr);
        return NULL;
    }
    return frr;
}

void fenwick_rr_destroy(fenwick_range_range_t* frr) {
    if (frr) {
        fenwick_destroy(frr->t1);
        fenwick_destroy(frr->t2);
        free(frr);
    }
}

static long long fenwick_rr_prefix(const fenwick_range_range_t* frr, size_t idx) {
    long long sum1 = fenwick_query_prefix(frr->t1, idx);
    long long sum2 = fenwick_query_prefix(frr->t2, idx);
    return sum1 * (long long)(idx + 1) - sum2;
}

bool fenwick_rr_add(fenwick_range_range_t* frr, size_t left, size_t right, long long val) {
    if (!frr || left > right || right >= frr->size) return false;
    fenwick_add(frr->t1, left, val);
    fenwick_add(frr->t2, left, val * (long long)left);

    if (right + 1 < frr->size) {
        fenwick_add(frr->t1, right + 1, -val);
        fenwick_add(frr->t2, right + 1, -val * (long long)(right + 1));
    }
    return true;
}

long long fenwick_rr_query(const fenwick_range_range_t* frr, size_t left, size_t right) {
    if (!frr || left > right || right >= frr->size) return 0;
    if (left == 0) return fenwick_rr_prefix(frr, right);
    return fenwick_rr_prefix(frr, right) - fenwick_rr_prefix(frr, left - 1);
}
