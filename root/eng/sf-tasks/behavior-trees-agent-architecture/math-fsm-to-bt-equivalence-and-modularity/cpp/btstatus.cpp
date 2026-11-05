// Статична реалізація через поліморфізм без динамічної пам'яті на C++
enum class BtStatus {
    Success,
    Failure,
    Running
};

class BtNode {
public:
    virtual BtStatus tick() = 0;
};

template<size_t N>
class Selector : public BtNode {
    BtNode* children[N];
public:
    Selector(BtNode* (&nodes)[N]) {
        for(size_t i = 0; i < N; ++i) {
            children[i] = nodes[i];
        }
    }

    BtStatus tick() override {
        for (size_t i = 0; i < N; i++) {
            BtStatus status = children[i]->tick();
            if (status != BtStatus::Failure) {
                return status;
            }
        }
        return BtStatus::Failure;
    }
};
