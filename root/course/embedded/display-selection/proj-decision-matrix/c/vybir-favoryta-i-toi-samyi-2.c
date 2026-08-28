int pick_winner(const Criterion *crit, int n_crit,
                const Candidate *cand, int n_cand)
{
    int      best_i = 0;
    uint32_t best_s = 0;
    for (int i = 0; i < n_cand; i++) {
        uint32_t s = weighted_sum(crit, n_crit, &cand[i]);
        printf("  %-8s S = %u\n", cand[i].name, s);
        if (s > best_s) {          /* строго >: за рівності лишаємо
                                      першого — про це нижче */
            best_s = s;
            best_i = i;
        }
    }
    return best_i;
}
