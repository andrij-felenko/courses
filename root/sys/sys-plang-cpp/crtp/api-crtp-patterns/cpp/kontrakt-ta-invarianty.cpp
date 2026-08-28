template <typename Derived>
class StaticVisitor {
public:
    template <typename NodeTy>
    void dispatch(NodeTy& node) {
        Derived& self = *static_cast<Derived*>(this);
        self.handle(node);
    }
};

struct ASTNodeA {};
struct ASTNodeB {};

class ASTInspector : public StaticVisitor<ASTInspector> {
public:
    void handle(ASTNodeA& a) {
        std::cout << "Inspecting ASTNodeA\n";
    }
    void handle(ASTNodeB& b) {
        std::cout << "Inspecting ASTNodeB\n";
    }
};
