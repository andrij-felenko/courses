/**
 * Диспетчер оптимістичних мутацій на C++ (Modern C++20)
 */

#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
#include <memory>
#include <functional>
#include <algorithm>
#include <chrono>
#include <optional>

struct Entity {
    std::string id;
    std::string title;
    bool completed{false};
    std::optional<std::string> parentId;
};

struct State {
    std::unordered_map<std::string, Entity> entities;
};

enum class MutationType { CREATE, UPDATE, DELETE_OP };

struct Mutation {
    std::string id;
    MutationType type;
    std::string entityId;
    std::optional<std::string> tempId;
    Entity payload;
    std::chrono::system_clock::time_point timestamp;
    bool aborted{false};
    int retries{0};
};

struct ServerResponse {
    bool success{false};
    std::optional<std::string> tempId;
    std::optional<std::string> serverId;
    int statusCode{200};
    std::string errorMessage;
};

class OptimisticMutationManager {
public:
    using StateListener = std::function<void(const State&)>;
    using NetworkExecutor = std::function<ServerResponse(const Mutation&)>;

    explicit OptimisticMutationManager(State initial = {})
        : canonicalState_(std::move(initial)) {}

    void subscribe(StateListener listener) {
        listeners_.push_back(listener);
        listener(getViewState());
    }

    std::string resolveId(const std::string& id) const {
        auto it = idMap_.find(id);
        if (it != idMap_.end()) return it->second;
        return id;
    }

    State getViewState() const {
        State view = canonicalState_;
        for (const auto& mut : pendingQueue_) {
            if (!mut.aborted) {
                applyMutation(view, mut);
            }
        }
        return view;
    }

    void dispatch(MutationType type,
                  const std::string& entityId,
                  Entity payload,
                  const NetworkExecutor& executor) {
        std::string mutId = "mut_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count());
        std::optional<std::string> tempId = (type == MutationType::CREATE) ? std::make_optional(entityId) : std::nullopt;

        // Захист від гонок: скасовуємо незавершені попередні UPDATE для тієї ж сутності
        std::string resolvedTarget = resolveId(entityId);
        for (auto& prev : pendingQueue_) {
            if (resolveId(prev.entityId) == resolvedTarget && prev.type == MutationType::UPDATE) {
                prev.aborted = true;
            }
        }

        Mutation mut{
            mutId,
            type,
            entityId,
            tempId,
            std::move(payload),
            std::chrono::system_clock::now(),
            false,
            0
        };

        // 1. Оптимістично додаємо в чергу
        pendingQueue_.push_back(mut);
        notify(); // UI оновлюється миттєво

        // 2. Виконання запиту в мережі
        executeMutation(pendingQueue_.back(), executor);
    }

private:
    State canonicalState_;
    std::vector<Mutation> pendingQueue_;
    std::unordered_map<std::string, std::string> idMap_;
    std::vector<StateListener> listeners_;

    void notify() {
        State currentView = getViewState();
        for (auto& l : listeners_) {
            l(currentView);
        }
    }

    void applyMutation(State& state, const Mutation& mutation) const {
        std::string targetId = resolveId(mutation.entityId);
        std::optional<std::string> resolvedParent = mutation.payload.parentId
            ? std::make_optional(resolveId(*mutation.payload.parentId))
            : std::nullopt;

        switch (mutation.type) {
            case MutationType::CREATE: {
                std::string id = mutation.tempId.value_or(targetId);
                state.entities[id] = Entity{
                    id,
                    mutation.payload.title,
                    mutation.payload.completed,
                    resolvedParent
                };
                break;
            }
            case MutationType::UPDATE: {
                auto it = state.entities.find(targetId);
                if (it != state.entities.end()) {
                    it->second.title = mutation.payload.title;
                    it->second.completed = mutation.payload.completed;
                    it->second.parentId = resolvedParent;
                }
                break;
            }
            case MutationType::DELETE_OP: {
                state.entities.erase(targetId);
                break;
            }
        }
    }

    void executeMutation(Mutation& mutation, const NetworkExecutor& executor) {
        if (mutation.aborted) {
            removeMutation(mutation.id);
            return;
        }

        ServerResponse resp = executor(mutation);

        if (resp.success) {
            if (mutation.tempId && resp.serverId) {
                idMap_[*mutation.tempId] = *resp.serverId;
                mutation.entityId = *resp.serverId;
            }
            // Фіксуємо зміну в канонічному стані
            applyMutation(canonicalState_, mutation);
            removeMutation(mutation.id);
            notify();
        } else {
            if (resp.statusCode >= 400 && resp.statusCode < 500 && resp.statusCode != 408) {
                // Фатальна помилка -> REBASE: просто видаляємо з черги
                std::cerr << "[OptimisticManager] Rollback: " << resp.errorMessage << "\n";
                removeMutation(mutation.id);
                notify();
            } else {
                // Мережевий збій -> повтор або відкат після ліміту
                mutation.retries++;
                if (mutation.retries > 3) {
                    removeMutation(mutation.id);
                    notify();
                }
            }
        }
    }

    void removeMutation(const std::string& id) {
        pendingQueue_.erase(
            std::remove_if(pendingQueue_.begin(), pendingQueue_.end(),
                           [&](const Mutation& m) { return m.id == id; }),
            pendingQueue_.end()
        );
    }
};
