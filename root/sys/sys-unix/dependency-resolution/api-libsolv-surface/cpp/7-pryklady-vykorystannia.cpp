#include <iostream>
#include <memory>
#include <vector>
#include <string_view>
#include <stdexcept>

#include <solv/pool.h>
#include <solv/repo.h>
#include <solv/solver.h>
#include <solv/selection.h>
#include <solv/transaction.h>

// RAII обгортка для libsolv Pool
struct LibsolvPoolDeleter {
    void operator()(Pool* p) const noexcept {
        if (p) pool_free(p);
    }
};
using UniquePool = std::unique_ptr<Pool, LibsolvPoolDeleter>;

// RAII обгортка для libsolv Solver
struct LibsolvSolverDeleter {
    void operator()(Solver* s) const noexcept {
        if (s) solver_free(s);
    }
};
using UniqueSolver = std::unique_ptr<Solver, LibsolvSolverDeleter>;

// RAII обгортка для libsolv Transaction
struct LibsolvTransactionDeleter {
    void operator()(Transaction* t) const noexcept {
        if (t) transaction_free(t);
    }
};
using UniqueTransaction = std::unique_ptr<Transaction, LibsolvTransactionDeleter>;

// RAII обгортка для черги Queue
class SolvQueue {
public:
    SolvQueue() { queue_init(&q_); }
    ~SolvQueue() { queue_free(&q_); }

    SolvQueue(const SolvQueue&) = delete;
    SolvQueue& operator=(const SolvQueue&) = delete;

    void push(Id flag, Id id) {
        queue_push2(&q_, flag, id);
    }

    Queue* raw() noexcept { return &q_; }

private:
    Queue q_;
};

class PackageSolverEngine {
public:
    PackageSolverEngine() : pool_(pool_create()) {
        if (!pool_) {
            throw std::runtime_error("Не вдалося ініціалізувати libsolv Pool");
        }
    }

    void add_package(std::string_view repo_name, std::string_view pkg_name, std::string_view version, std::string_view arch) {
        Repo* repo = repo_create(pool_.get(), repo_name.data());
        Id id = repo_add_solvable(repo);
        
        Solvable* s = pool_id2solvable(pool_.get(), id);
        s->name = pool_str2id(pool_.get(), pkg_name.data(), 1);
        s->evr = pool_str2id(pool_.get(), version.data(), 1);
        s->arch = pool_str2id(pool_.get(), arch.data(), 1);
        
        last_pkg_id_ = id;
    }

    void solve_installation() {
        pool_createwhatprovides(pool_.get());

        SolvQueue queue;
        queue.push(SOLVER_INSTALL | SOLVER_SOLVABLE, last_pkg_id_);

        UniqueSolver solver(solver_create(pool_.get()));
        int problems = solver_solve(solver.get(), queue.raw());

        if (problems > 0) {
            std::cout << "[libsolv C++] Виявлено " << problems << " конфліктів у транзакції:\n";
            for (int p = 1; p <= problems; ++p) {
                Id rule = solver_findproblemrule(solver.get(), p);
                std::cout << "  - " << solver_problemrule2str(solver.get(), rule) << "\n";
            }
            throw std::runtime_error("Не вдалося розв'язати залежності транзакції");
        }

        UniqueTransaction trans(solver_create_transaction(solver.get()));
        std::cout << "[libsolv C++] Транзакція успішна! Кількість дій: " << trans->steps.count << "\n";
    }

private:
    UniquePool pool_;
    Id last_pkg_id_{0};
};
