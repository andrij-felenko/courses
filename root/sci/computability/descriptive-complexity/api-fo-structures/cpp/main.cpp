// =========================================================================
// 1. УПРАВЛІННЯ РЕЛЯЦІЙНИМИ СТРУКТУРАМИ ТА AST-ВУЗЛАМИ У C++
// =========================================================================

namespace fo_logic {

enum class NodeType : uint8_t {
    PredRel, PredEq, PredLt, Not, And, Or, Implies, Exists, ForAll, Lfp, Tc
};

class Structure {
public:
    explicit Structure(size_t domain_size, bool has_order = false);
    ~Structure() = default;

    Structure(const Structure&) = delete;
    Structure& operator=(const Structure&) = delete;
    Structure(Structure&&) noexcept = default;
    Structure& operator=(Structure&&) noexcept = default;

    size_t add_relation(std::string_view name, size_t arity);
    bool add_tuple(size_t relation_idx, const std::vector<size_t>& tuple);

    [[nodiscard]] size_t domain_size() const noexcept;
    [[nodiscard]] bool has_order() const noexcept;
    [[nodiscard]] bool contains_tuple(size_t relation_idx, const std::vector<size_t>& tuple) const;

private:
    struct Relation {
        std::string name;
        size_t arity;
        std::vector<size_t> flat_tuples;
    };
    size_t domain_size_;
    bool has_order_;
    std::vector<Relation> relations_;
};

class Environment {
public:
    Environment() = default;
    void bind(int var_id, size_t val) { bindings_[var_id] = val; }
    [[nodiscard]] size_t get(int var_id) const { return bindings_.at(var_id); }
    void unbind(int var_id) { bindings_.erase(var_id); }

private:
    std::unordered_map<int, size_t> bindings_;
};

class ASTNode {
public:
    virtual ~ASTNode() = default;
    [[nodiscard]] virtual NodeType type() const noexcept = 0;
    [[nodiscard]] virtual bool evaluate(const Structure& st, Environment& env) const = 0;
};

using NodePtr = std::unique_ptr<ASTNode>;

NodePtr make_relation_pred(size_t rel_idx, std::vector<int> var_ids);
NodePtr make_eq_pred(int var1, int var2);
NodePtr make_lt_pred(int var1, int var2);
NodePtr make_not(NodePtr child);
NodePtr make_and(NodePtr left, NodePtr right);
NodePtr make_or(NodePtr left, NodePtr right);
NodePtr make_exists(int var_id, NodePtr body);
NodePtr make_forall(int var_id, NodePtr body);

class ModelChecker {
public:
    explicit ModelChecker(const Structure& st) : structure_(st) {}

    [[nodiscard]] bool verify(const ASTNode& formula) {
        Environment env;
        return formula.evaluate(structure_, env);
    }

private:
    const Structure& structure_;
};

} // namespace fo_logic
