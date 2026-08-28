#include <bits/stdc++.h>
using namespace std;

struct Gate { bool is_and; vector<string> in; };
using Tree = map<string, Gate>;
using Cut  = set<string>;                       // переріз = набір імен

set<Cut> mocus(const Tree& tree, const string& top) {
    vector<Cut> work{ Cut{top} };               // рядки з вентилями (черга роботи)
    set<Cut> cuts;                              // рядки з самих базових подій
    while (!work.empty()) {
        Cut row = move(work.back()); work.pop_back();
        string gate;
        for (const auto& s : row)
            if (tree.count(s)) { gate = s; break; }
        if (gate.empty()) { cuts.insert(move(row)); continue; }   // переріз-кандидат
        row.erase(gate);
        const Gate& g = tree.at(gate);
        if (g.is_and) {                         // І — дописати стовпці
            row.insert(g.in.begin(), g.in.end());
            work.push_back(move(row));
        } else {                                // АБО — розмножити рядки
            for (const auto& s : g.in) {
                Cut r = row; r.insert(s);
                work.push_back(move(r));
            }
        }
    }
    return cuts;
}

vector<Cut> minimal(const set<Cut>& cuts) {
    vector<Cut> all(cuts.begin(), cuts.end());
    stable_sort(all.begin(), all.end(),
                [](const Cut& a, const Cut& b){ return a.size() < b.size(); });
    vector<Cut> out;                            // поглинання
    for (const auto& c : all) {
        bool dominated = false;
        for (const auto& m : out)               // m ⊆ c  ⇒  c немінімальний
            if (includes(c.begin(), c.end(), m.begin(), m.end())) { dominated = true; break; }
        if (!dominated) out.push_back(c);
    }
    return out;
}

int main() {
    Tree tree = {
        {"TOP",   {false, {"POWER", "PUMPS"}}},
        {"PUMPS", {true,  {"PUMP_A", "PUMP_B"}}},
    };
    for (const auto& c : minimal(mocus(tree, "TOP"))) {
        for (const auto& s : c) cout << s << ' ';
        cout << '\n';
    }
    // POWER
    // PUMP_A PUMP_B
}
