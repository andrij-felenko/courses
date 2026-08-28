uint32_t weighted_sum(const Criterion *crit, int n_crit,
                       const Candidate *cand)
{
    uint32_t s = 0;
    for (int i = 0; i < n_crit; i++) {
        /* добуток рахуємо в 32 бітах: (uint32_t)weight змушує
           все множення йти в ширшому типі, не в uint8_t */
        s += (uint32_t)crit[i].weight * cand->score[i];
    }
    return s;
}
