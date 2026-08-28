int main() {
    const Item alice{7}, badge{8};

    auto make  = []  { Roster r; r.enroll(Item{1}, Item{2});
                                 r.enroll(Item{3}, Item{4}); return r; };
    auto op    = [&](Roster& r) { r.enroll(alice, badge); };
    auto holds = [] (const Roster& r) { return r.invariant(); };

    long long k = sweep(make, op, holds, /*strong=*/false);
    std::printf("точок кидання в enroll: %lld\n", k);
}
