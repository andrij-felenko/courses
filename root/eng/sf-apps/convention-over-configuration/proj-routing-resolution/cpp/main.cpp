#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <optional>
#include <functional>

enum class NodeType {
    Static,
    Param
};

using ParamMap = std::unordered_map<std::string, std::string>;
using RouteHandler = std::function<void(const ParamMap&)>;

struct RouteNode {
    std::string name;
    NodeType type;
    std::optional<RouteHandler> handler;
    std::vector<std::unique_ptr<RouteNode>> children;

    RouteNode(std::string node_name, NodeType node_type, std::optional<RouteHandler> h = std::nullopt)
        : name(std::move(node_name)), type(node_type), handler(std::move(h)) {}

    RouteNode* add_child(std::string child_name, NodeType child_type, std::optional<RouteHandler> h = std::nullopt) {
        children.push_back(std::make_unique<RouteNode>(std::move(child_name), child_type, std::move(h)));
        return children.back().get();
    }
};

class FileSystemRouter {
public:
    FileSystemRouter() : root_("", NodeType::Static) {}

    RouteNode* root() { return &root_; }

    bool dispatch(std::string_view url_path) const {
        std::vector<std::string_view> segments = tokenize(url_path);
        ParamMap params;
        return resolve(&root_, segments, 0, params);
    }

private:
    RouteNode root_;

    static std::vector<std::string_view> tokenize(std::string_view path) {
        std::vector<std::string_view> result;
        size_t start = 0;
        while (start < path.size()) {
            start = path.find_first_not_of('/', start);
            if (start == std::string_view::npos) break;
            size_t end = path.find_first_of('/', start);
            if (end == std::string_view::npos) {
                result.push_back(path.substr(start));
                break;
            }
            result.push_back(path.substr(start, end - start));
            start = end;
        }
        return result;
    }

    bool resolve(const RouteNode* current, const std::vector<std::string_view>& segments,
                 size_t index, ParamMap& params) const {
        if (index == segments.size()) {
            if (current->handler.has_value()) {
                (*current->handler)(params);
                return true;
            }
            return false;
        }

        std::string_view current_seg = segments[index];

        // 1. Пріоритет: точний статичний збіг
        for (const auto& child : current->children) {
            if (child->type == NodeType::Static && child->name == current_seg) {
                if (resolve(child.get(), segments, index + 1, params)) {
                    return true;
                }
            }
        }

        // 2. Пріоритет: динамічний параметр [name]
        for (const auto& child : current->children) {
            if (child->type == NodeType::Param) {
                params[child->name] = std::string(current_seg);
                if (resolve(child.get(), segments, index + 1, params)) {
                    return true;
                }
                params.erase(child->name); // Відкат стану
            }
        }

        return false;
    }
};

int main() {
    FileSystemRouter router;

    auto* api = router.root()->add_child("api", NodeType::Static);
    auto* users = api->add_child("users", NodeType::Static);

    // Статичний маршрут: /api/users/settings
    users->add_child("settings", NodeType::Static, [](const ParamMap&) {
        std::cout << "-> [Handler] Статичний маршрут: Налаштування системи\n";
    });

    // Динамічний маршрут: /api/users/[userId]/profile
    auto* user_id = users->add_child("userId", NodeType::Param);
    user_id->add_child("profile", NodeType::Static, [](const ParamMap& params) {
        std::cout << "-> [Handler] Динамічний маршрут: Профіль користувача\n";
        for (const auto& [key, value] : params) {
            std::cout << "   Параметр [" << key << "] = " << value << "\n";
        }
    });

    // Динамічний вкладений маршрут: /api/users/[userId]/posts/[postId]
    auto* posts = user_id->add_child("posts", NodeType::Static);
    posts->add_child("postId", NodeType::Param, [](const ParamMap& params) {
        std::cout << "-> [Handler] Динамічний маршрут: Пост користувача\n";
        for (const auto& [key, value] : params) {
            std::cout << "   Параметр [" << key << "] = " << value << "\n";
        }
    });

    const std::vector<std::string_view> test_urls = {
        "/api/users/settings",
        "/api/users/1024/profile",
        "/api/users/42/posts/999",
        "/api/users/unknown/invalid/path"
    };

    for (const auto& url : test_urls) {
        std::cout << "=== Запит: " << url << " ===\n";
        if (!router.dispatch(url)) {
            std::cout << "-> Помилка 404: Відповідного маршруту не знайдено\n";
        }
        std::cout << "\n";
    }

    return 0;
}
