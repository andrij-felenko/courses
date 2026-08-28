#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <string_view>

struct RelationTuple {
    std::string object_id;
    std::string relation;
    std::string subject_id;
};

struct EvalContext {
    int current_time_hour;
    int allowed_start_hour = 8;
    int allowed_end_hour = 22;
};

class RebacAbacEngine {
private:
    std::unordered_map<std::string, std::vector<RelationTuple>> tuples_;

public:
    void add_tuple(std::string_view obj, std::string_view rel, std::string_view subj) {
        tuples_[std::string(obj)].push_back(RelationTuple{
            std::string(obj), std::string(rel), std::string(subj)
        });
    }

    bool check_rebac(std::string_view subject, std::string_view relation, std::string_view obj,
                     std::unordered_set<std::string>& visited) const {
        std::string state_key = std::string(obj) + "#" + std::string(relation) + "@" + std::string(subject);
        if (visited.find(state_key) != visited.end()) {
            return false; // Запобігання цикли у графі
        }
        visited.insert(state_key);

        auto it = tuples_.find(std::string(obj));
        if (it == tuples_.end()) return false;

        for (const auto& t : it->second) {
            if (t.relation != relation) continue;

            if (t.subject_id == subject) return true;

            auto hash_pos = t.subject_id.find('#');
            if (hash_pos != std::string::npos) {
                std::string parent_obj = t.subject_id.substr(0, hash_pos);
                std::string parent_rel = t.subject_id.substr(hash_pos + 1);
                if (check_rebac(subject, parent_rel, parent_obj, visited)) {
                    return true;
                }
            }
        }
        return false;
    }

    bool evaluate(std::string_view subject, std::string_view action, std::string_view obj, const EvalContext& ctx) const {
        std::unordered_set<std::string> visited;
        if (!check_rebac(subject, action, obj, visited)) {
            return false;
        }
        if (ctx.current_time_hour < ctx.allowed_start_hour || ctx.current_time_hour > ctx.allowed_end_hour) {
            return false;
        }
        return true;
    }
};

int main() {
    RebacAbacEngine engine;
    engine.add_tuple("home:101", "owner", "user:alice");
    engine.add_tuple("camera:704", "parent", "home:101");
    engine.add_tuple("camera:704", "viewer", "home:101#owner");

    EvalContext ctx_day{14, 8, 22};
    std::cout << "Day 14:00 access: " << (engine.evaluate("user:alice", "viewer", "camera:704", ctx_day) ? "ALLOW" : "DENY") << "\n";

    EvalContext ctx_night{23, 8, 22};
    std::cout << "Night 23:00 access: " << (engine.evaluate("user:alice", "viewer", "camera:704", ctx_night) ? "ALLOW" : "DENY") << "\n";
    return 0;
}
