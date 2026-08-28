#include <bits/stdc++.h>
using namespace std;

struct BDD {
    struct Node { int var, lo, hi; };
    unordered_map<string,int> rank;
    vector<Node> nodes;                          // nodes[id]; 0,1 — термінали
    map<array<int,3>,int> uniq;                  // (var,lo,hi) -> id   ← хеш-консинг
    map<array<int,3>,int> memo;                  // (op,a,b)   -> id    ← мемо apply

    explicit BDD(const vector<string>& order) {
        for (int i = 0; i < (int)order.size(); ++i) rank[order[i]] = i;
        nodes.push_back({-1,0,0});               // id 0 = FALSE
        nodes.push_back({-1,1,1});               // id 1 = TRUE
    }
    int mk(int var, int lo, int hi) {
        if (lo == hi) return lo;                 // надлишковий вузол
        array<int,3> key{var, lo, hi};
        if (auto it = uniq.find(key); it != uniq.end()) return it->second;
        int id = nodes.size();
        nodes.push_back({var, lo, hi});
        uniq[key] = id;
        return id;
    }
    int var(const string& name) { return mk(rank.at(name), 0, 1); }

    int apply(int op, int a, int b) {            // op: 0 = І, 1 = АБО
        if (op == 0) { if (a==0||b==0) return 0; if (a==1) return b; if (b==1) return a; }
        else         { if (a==1||b==1) return 1; if (a==0) return b; if (b==0) return a; }
        if (a == b) return a;
        if (a > b) swap(a, b);                   // комутативність
        array<int,3> key{op, a, b};
        if (auto it = memo.find(key); it != memo.end()) return it->second;
        int top = min(nodes[a].var, nodes[b].var);
        auto cof = [&](int n, int v) -> pair<int,int> {
            if (n > 1 && nodes[n].var == v) return {nodes[n].lo, nodes[n].hi};
            return {n, n};
        };
        auto [a0,a1] = cof(a, top);
        auto [b0,b1] = cof(b, top);
        int r = mk(top, apply(op, a0, b0), apply(op, a1, b1));
        return memo[key] = r;
    }
    double probability(int root, const vector<double>& p) {
        unordered_map<int,double> mp{{0, 0.0}, {1, 1.0}};
        function<double(int)> rec = [&](int n) -> double {
            if (auto it = mp.find(n); it != mp.end()) return it->second;
            const Node& d = nodes[n];
            return mp[n] = (1 - p[d.var]) * rec(d.lo) + p[d.var] * rec(d.hi);
        };
        return rec(root);
    }
};

struct Gate { bool is_and; vector<string> in; };
using Tree = map<string, Gate>;

int build(BDD& bdd, const Tree& tree, const string& node) {
    auto it = tree.find(node);
    if (it == tree.end()) return bdd.var(node);
    int op = it->second.is_and ? 0 : 1;
    const auto& in = it->second.in;
    int r = build(bdd, tree, in[0]);
    for (size_t i = 1; i < in.size(); ++i)
        r = bdd.apply(op, r, build(bdd, tree, in[i]));
    return r;
}

int main() {
    Tree tree = {
        {"TOP",   {false, {"POWER", "PUMPS"}}},
        {"PUMPS", {true,  {"PUMP_A", "PUMP_B"}}},
    };
    vector<string> order = {"POWER", "PUMP_A", "PUMP_B"};
    BDD bdd(order);
    int root = build(bdd, tree, "TOP");
    vector<double> p = {0.001, 0.01, 0.01};      // за порядком змінних
    printf("%.7f\n", bdd.probability(root, p));  // 0.0010999
}
