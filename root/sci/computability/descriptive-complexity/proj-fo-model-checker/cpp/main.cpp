// C++ Implementation: Object-Oriented Idiomatic FO Model Checker
#include <iostream>
#include <vector>
#include <memory>
#include <unordered_map>
#include <string>

class Graph {
public:
    explicit Graph(size_t vertices) : num_vertices_(vertices), adj_(vertices, std::vector<bool>(vertices, false)) {}

    void add_edge(size_t u, size_t v) {
        if (u < num_vertices_ && v < num_vertices_) {
            adj_[u][v] = true;
        }
    }

    [[nodiscard]] bool has_edge(size_t u, size_t v) const {
        if (u < num_vertices_ && v < num_vertices_) {
            return adj_[u][v];
        }
        return false;
    }

    [[nodiscard]] size_t size() const noexcept { return num_vertices_; }

private:
    size_t num_vertices_;
    std::vector<std::vector<bool>> adj_;
};

using Environment = std::unordered_map<int, size_t>;

class ASTNode {
public:
    virtual ~ASTNode() = default;
    [[nodiscard]] virtual bool evaluate(const Graph& g, Environment& env) const = 0;
};

class EdgePredicate : public ASTNode {
public:
    EdgePredicate(int u_var, int v_var) : u_var_(u_var), v_var_(v_var) {}

    bool evaluate(const Graph& g, Environment& env) const override {
        return g.has_edge(env.at(u_var_), env.at(v_var_));
    }

private:
    int u_var_;
    int v_var_;
};

class EqualityPredicate : public ASTNode {
public:
    EqualityPredicate(int u_var, int v_var) : u_var_(u_var), v_var_(v_var) {}

    bool evaluate(const Graph& g, Environment& env) const override {
        return env.at(u_var_) == env.at(v_var_);
    }

private:
    int u_var_;
    int v_var_;
};

class LogicalAnd : public ASTNode {
public:
    LogicalAnd(std::unique_ptr<ASTNode> left, std::unique_ptr<ASTNode> right)
        : left_(std::move(left)), right_(std::move(right)) {}

    bool evaluate(const Graph& g, Environment& env) const override {
        return left_->evaluate(g, env) && right_->evaluate(g, env);
    }

private:
    std::unique_ptr<ASTNode> left_;
    std::unique_ptr<ASTNode> right_;
};

class LogicalNot : public ASTNode {
public:
    explicit LogicalNot(std::unique_ptr<ASTNode> child) : child_(std::move(child)) {}

    bool evaluate(const Graph& g, Environment& env) const override {
        return !child_->evaluate(g, env);
    }

private:
    std::unique_ptr<ASTNode> child_;
};

class ExistsQuantifier : public ASTNode {
public:
    ExistsQuantifier(int var_id, std::unique_ptr<ASTNode> body)
        : var_id_(var_id), body_(std::move(body)) {}

    bool evaluate(const Graph& g, Environment& env) const override {
        for (size_t val = 0; val < g.size(); ++val) {
            env[var_id_] = val;
            if (body_->evaluate(g, env)) {
                return true;
            }
        }
        return false;
    }

private:
    int var_id_;
    std::unique_ptr<ASTNode> body_;
};

class ForAllQuantifier : public ASTNode {
public:
    ForAllQuantifier(int var_id, std::unique_ptr<ASTNode> body)
        : var_id_(var_id), body_(std::move(body)) {}

    bool evaluate(const Graph& g, Environment& env) const override {
        for (size_t val = 0; val < g.size(); ++val) {
            env[var_id_] = val;
            if (!body_->evaluate(g, env)) {
                return false;
            }
        }
        return true;
    }

private:
    int var_id_;
    std::unique_ptr<ASTNode> body_;
};

int main() {
    Graph g(4);
    g.add_edge(0, 1);
    g.add_edge(1, 2);
    g.add_edge(2, 0);

    // Formulate ∃x ∃y ∃z (E(x,y) ∧ E(y,z) ∧ E(z,x))
    auto e_xy = std::make_unique<EdgePredicate>(0, 1);
    auto e_yz = std::make_unique<EdgePredicate>(1, 2);
    auto e_zx = std::make_unique<EdgePredicate>(2, 0);

    auto conj1 = std::make_unique<LogicalAnd>(std::move(e_xy), std::move(e_yz));
    auto conj2 = std::make_unique<LogicalAnd>(std::move(conj1), std::move(e_zx));

    auto exists_z = std::make_unique<ExistsQuantifier>(2, std::move(conj2));
    auto exists_y = std::make_unique<ExistsQuantifier>(1, std::move(exists_z));
    auto exists_x = std::make_unique<ExistsQuantifier>(0, std::move(exists_y));

    Environment env;
    bool has_k3 = exists_x->evaluate(g, env);

    std::cout << "Результат перевірки формули K3 (C++): " << (has_k3 ? "TRUE" : "FALSE") << "\n";

    return 0;
}
