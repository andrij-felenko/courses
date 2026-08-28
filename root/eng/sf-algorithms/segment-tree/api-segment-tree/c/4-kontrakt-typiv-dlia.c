typedef struct {
    long long sum;   /* Загальна сума елементів */
    long long pref;  /* Максимальна сума на префіксі */
    long long suff;  /* Максимальна сума на суфіксі */
    long long ans;   /* Максимальна сума на підвідрізку */
} kadane_node_t;

kadane_node_t combine_kadane(kadane_node_t left, kadane_node_t right) {
    kadane_node_t res;
    res.sum = left.sum + right.sum;
    res.pref = (left.pref > left.sum + right.pref) ? left.pref : left.sum + right.pref;
    res.suff = (right.suff > right.sum + left.suff) ? right.suff : right.sum + left.suff;
    
    long long m1 = (left.ans > right.ans) ? left.ans : right.ans;
    long long m2 = left.suff + right.pref;
    res.ans = (m1 > m2) ? m1 : m2;
    return res;
}
