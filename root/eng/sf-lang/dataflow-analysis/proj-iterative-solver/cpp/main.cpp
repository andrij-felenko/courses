#include <iostream>
#include <vector>
#include <queue>
#include <bitset>
#include <cstdint>

constexpr size_t MAX_VARS = 64;
using BitSet = std::bitset<MAX_VARS>;

struct Block {
    int id{0};
    BitSet use{};
    BitSet def{};
    BitSet in{};
    BitSet out{};

    std::vector<int> succ{};
    std::vector<int> pred{};
};

class DataflowSolver {
public:
    explicit DataflowSolver(size_t num_blocks, size_t num_vars)
        : num_vars_(num_vars), blocks_(num_blocks) {
        for (size_t i = 0; i < num_blocks; ++i) {
            blocks_[i].id = static_cast<int>(i);
        }
    }

    void add_edge(size_t from, size_t to) {
        blocks_[from].succ.push_back(static_cast<int>(to));
        blocks_[to].pred.push_back(static_cast<int>(from));
    }

    Block& block(size_t index) {
        return blocks_[index];
    }

    const Block& block(size_t index) const {
        return blocks_[index];
    }

    void solve_live_variables() {
        std::queue<int> worklist;
        std::vector<bool> in_worklist(blocks_.size(), true);

        for (const auto& b : blocks_) {
            worklist.push(b.id);
        }

        while (!worklist.empty()) {
            int b_id = worklist.front();
            worklist.pop();
            in_worklist[b_id] = false;
            auto& b = blocks_[b_id];

            // OUT[B] = ∪ IN[Succ]
            BitSet new_out{};
            for (int s_id : b.succ) {
                new_out |= blocks_[s_id].in;
            }
            b.out = new_out;

            // IN[B] = USE[B] ∪ (OUT[B] \ DEF[B])
            BitSet new_in = b.use | (b.out & ~b.def);

            if (new_in != b.in) {
                b.in = new_in;
                for (int p_id : b.pred) {
                    if (!in_worklist[p_id]) {
                        worklist.push(p_id);
                        in_worklist[p_id] = true;
                    }
                }
            }
        }
    }

    void print() const {
        std::cout << "=== Результати аналізу Live Variables (C++) ===\n";
        for (const auto& b : blocks_) {
            std::cout << "Блок B" << b.id << ":\n";
            std::cout << "  USE: { ";
            for (size_t v = 0; v < num_vars_; ++v) {
                if (b.use.test(v)) std::cout << "v" << v << " ";
            }
            std::cout << "}\n  DEF: { ";
            for (size_t v = 0; v < num_vars_; ++v) {
                if (b.def.test(v)) std::cout << "v" << v << " ";
            }
            std::cout << "}\n  IN : { ";
            for (size_t v = 0; v < num_vars_; ++v) {
                if (b.in.test(v)) std::cout << "v" << v << " ";
            }
            std::cout << "}\n  OUT: { ";
            for (size_t v = 0; v < num_vars_; ++v) {
                if (b.out.test(v)) std::cout << "v" << v << " ";
            }
            std::cout << "}\n\n";
        }
    }

private:
    size_t num_vars_{0};
    std::vector<Block> blocks_{};
};

int main() {
    DataflowSolver solver(4, 3);

    // B0 (Entry): def = {v0, v1} (a = 1; b = 2;)
    solver.block(0).def.set(0);
    solver.block(0).def.set(1);

    // B1 (Loop Header): use = {v0}, def = {v2} (c = a + 1; if ...)
    solver.block(1).use.set(0);
    solver.block(1).def.set(2);

    // B2 (Loop Body): use = {v1, v2}, def = {v0} (a = b + c;)
    solver.block(2).use.set(1);
    solver.block(2).use.set(2);
    solver.block(2).def.set(0);

    // B3 (Exit): use = {v2} (return c;)
    solver.block(3).use.set(2);

    // Ребра: B0 -> B1; B1 -> B2, B1 -> B3; B2 -> B1
    solver.add_edge(0, 1);
    solver.add_edge(1, 2);
    solver.add_edge(1, 3);
    solver.add_edge(2, 1);

    solver.solve_live_variables();
    solver.print();

    return 0;
}
