enum class Status { Success, Failure, Running };

class Node {
public:
    virtual Status tick() = 0;
};

class Selector : public Node {
    Node** children;
    size_t childCount;
public:
    Selector(Node** c, size_t count) : children(c), childCount(count) {}
    
    Status tick() override {
        for (size_t i = 0; i < childCount; ++i) {
            Status s = children[i]->tick();
            if (s != Status::Failure) {
                return s;
            }
        }
        return Status::Failure;
    }
};
