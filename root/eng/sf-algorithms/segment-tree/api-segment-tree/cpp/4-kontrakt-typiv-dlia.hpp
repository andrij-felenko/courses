struct KadaneNode {
    long long sum{0};
    long long pref{0};
    long long suff{0};
    long long ans{0};
};

struct KadaneCombine {
    KadaneNode operator()(const KadaneNode& left, const KadaneNode& right) const noexcept {
        KadaneNode res;
        res.sum = left.sum + right.sum;
        res.pref = std::max(left.pref, left.sum + right.pref);
        res.suff = std::max(right.suff, right.sum + left.suff);
        res.ans = std::max({left.ans, right.ans, left.suff + right.pref});
        return res;
    }
};
