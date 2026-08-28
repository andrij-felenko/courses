#include <memory>
#include <iostream>

class WorkerNode : public std::enable_shared_from_this<WorkerNode> {
public:
    void register_in_cluster() {
        std::shared_ptr<WorkerNode> self_ptr = shared_from_this();
        std::cout << "Node registered with use_count: " << self_ptr.use_count() << "\n";
    }
};
