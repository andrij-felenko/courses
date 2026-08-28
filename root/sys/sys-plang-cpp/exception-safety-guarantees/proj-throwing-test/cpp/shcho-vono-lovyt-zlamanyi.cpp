#include <vector>

using Item = Probe</*NothrowMove=*/true>;
template <class T> using Vec = std::vector<T, Probing<T>>;

class Roster {
    Vec<Item> people_;
    Vec<Item> badges_;
public:
    // Інваріант класу: у кожної людини рівно один жетон.
    bool invariant() const { return people_.size() == badges_.size(); }

    void enroll(const Item& person, const Item& badge) {
        people_.push_back(person);
        badges_.push_back(badge);   // ← кине тут — і людина лишиться без жетона
    }

    friend bool operator==(const Roster& a, const Roster& b) {
        return a.people_ == b.people_ && a.badges_ == b.badges_;
    }
};
