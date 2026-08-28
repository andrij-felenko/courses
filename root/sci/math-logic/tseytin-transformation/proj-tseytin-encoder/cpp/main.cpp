#include <iostream>
#include <vector>
#include <memory>
#include <string>

enum class NodeType {
    Var,
    Not,
    And,
    Or,
    Implies,
    Xor
};

// Ідіоматична ієрархія вузлів AST з RAII керуванням пам'яттю
class ASTNode {
public:
    virtual ~ASTNode() = default;
    virtual NodeType getType() const = 0;
};

class VarNode : public ASTNode {
    int m_varId;
public:
    explicit VarNode(int id) : m_varId(id) {}
    NodeType getType() const override { return NodeType::Var; }
    int getId() const { return m_varId; }
};

class UnaryNode : public ASTNode {
    NodeType m_type;
    std::unique_ptr<ASTNode> m_child;
public:
    UnaryNode(NodeType type, std::unique_ptr<ASTNode> child)
        : m_type(type), m_child(std::move(child)) {}
    NodeType getType() const override { return m_type; }
    const ASTNode* getChild() const { return m_child.get(); }
};

class BinaryNode : public ASTNode {
    NodeType m_type;
    std::unique_ptr<ASTNode> m_left;
    std::unique_ptr<ASTNode> m_right;
public:
    BinaryNode(NodeType type, std::unique_ptr<ASTNode> left, std::unique_ptr<ASTNode> right)
        : m_type(type), m_left(std::move(left)), m_right(std::move(right)) {}
    NodeType getType() const override { return m_type; }
    const ASTNode* getLeft() const { return m_left.get(); }
    const ASTNode* getRight() const { return m_right.get(); }
};

// Клас кодера Цейтіна
class TseytinEncoder {
    using Clause = std::vector<int>;
    std::vector<Clause> m_clauses;
    int m_maxVar;

public:
    explicit TseytinEncoder(int numInputs) : m_maxVar(numInputs) {}

    int freshVar() {
        return ++m_maxVar;
    }

    void addClause(Clause clause) {
        m_clauses.push_back(std::move(clause));
    }

    int transform(const ASTNode* node) {
        if (!node) return 0;

        if (node->getType() == NodeType::Var) {
            return static_cast<const VarNode*>(node)->getId();
        }

        if (node->getType() == NodeType::Not) {
            auto unary = static_cast<const UnaryNode*>(node);
            int childVar = transform(unary->getChild());
            int outVar = freshVar();
            
            // outVar <-> NOT childVar
            addClause({-outVar, -childVar});
            addClause({outVar, childVar});
            return outVar;
        }

        auto binary = static_cast<const BinaryNode*>(node);
        int leftVar = transform(binary->getLeft());
        int rightVar = transform(binary->getRight());
        int outVar = freshVar();

        switch (node->getType()) {
            case NodeType::And:
                // outVar <-> (leftVar AND rightVar)
                addClause({-outVar, leftVar});
                addClause({-outVar, rightVar});
                addClause({outVar, -leftVar, -rightVar});
                break;

            case NodeType::Or:
                // outVar <-> (leftVar OR rightVar)
                addClause({outVar, -leftVar});
                addClause({outVar, -rightVar});
                addClause({-outVar, leftVar, rightVar});
                break;

            case NodeType::Implies:
                // outVar <-> (leftVar -> rightVar)
                addClause({outVar, leftVar});
                addClause({outVar, -rightVar});
                addClause({-outVar, -leftVar, rightVar});
                break;

            case NodeType::Xor:
                // outVar <-> (leftVar XOR rightVar)
                addClause({-outVar, -leftVar, -rightVar});
                addClause({-outVar, leftVar, rightVar});
                addClause({outVar, -leftVar, rightVar});
                addClause({outVar, leftVar, -rightVar});
                break;

            default:
                break;
        }

        return outVar;
    }

    void exportDimacs(std::ostream& os, int rootVar) const {
        os << "p cnf " << m_maxVar << " " << (m_clauses.size() + 1) << "\n";
        for (const auto& clause : m_clauses) {
            for (int lit : clause) {
                os << lit << " ";
            }
            os << "0\n";
        }
        os << rootVar << " 0\n";
    }
};

int main() {
    // Вхідні змінні: 1=A, 2=B, 3=C
    auto varA = std::make_unique<VarNode>(1);
    auto varB = std::make_unique<VarNode>(2);
    auto varC = std::make_unique<VarNode>(3);

    auto andNode = std::make_unique<BinaryNode>(NodeType::And, std::move(varA), std::move(varB));
    auto notNode = std::make_unique<UnaryNode>(NodeType::Not, std::move(varC));
    auto root = std::make_unique<BinaryNode>(NodeType::Or, std::move(andNode), std::move(notNode));

    TseytinEncoder encoder(3);
    int rootVar = encoder.transform(root.get());

    std::cout << "c C++ Tseytin Encoder DIMACS Output\n";
    encoder.exportDimacs(std::cout, rootVar);

    return 0;
}
