#include <assert.h>

void validate_matrix(const Criterion *crit, int n_crit,
                     const Candidate *cand, int n_cand)
{
    assert(n_crit > 0 && n_crit <= MAX_CRIT);
    assert(n_cand > 0 && n_cand <= MAX_CAND);
    for (int i = 0; i < n_cand; i++)
        for (int j = 0; j < n_crit; j++)
            /* оцінка мусить бути в межах шкали 1..5 */
            assert(cand[i].score[j] >= 1 && cand[i].score[j] <= 5);
}
