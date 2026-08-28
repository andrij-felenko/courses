#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <optional>
#include <variant>
#include <functional>
#include <array>

namespace lwm2m {

enum class Operation : uint8_t {
    Read    = 0x01,
    Write   = 0x02,
    Execute = 0x04
};

constexpr Operation operator|(Operation a, Operation b) noexcept {
    return static_cast<Operation>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}

constexpr bool has_op(Operation mask, Operation query) noexcept {
    return (static_cast<uint8_t>(mask) & static_cast<uint8_t>(query)) != 0;
}

using ExecHandler = void(*)();

using ResourceValue = std::variant<
    int64_t,
    float,
    bool,
    std::string_view,
    std::span<const uint8_t>,
    ExecHandler
>;

struct Resource {
    uint16_t id{0};
    Operation ops{Operation::Read};
    ResourceValue value{};
};

struct Instance {
    uint16_t id{0};
    std::span<Resource> resources{};
};

struct Object {
    uint16_t id{0};
    std::span<Instance> instances{};
};

class ClientEngine {
public:
    explicit constexpr ClientEngine(std::span<Object> registry) noexcept : registry_(registry) {}

    [[nodiscard]] std::optional<ResourceValue> read(uint16_t obj_id, uint16_t inst_id, uint16_t res_id) const noexcept {
        const auto* res = find_resource(obj_id, inst_id, res_id);
        if (res != nullptr && has_op(res->ops, Operation::Read)) {
            return res->value;
        }
        return std::nullopt;
    }

    [[nodiscard]] bool execute(uint16_t obj_id, uint16_t inst_id, uint16_t res_id) const noexcept {
        const auto* res = find_resource(obj_id, inst_id, res_id);
        if (res != nullptr && has_op(res->ops, Operation::Execute)) {
            if (std::holds_alternative<ExecHandler>(res->value)) {
                auto handler = std::get<ExecHandler>(res->value);
                if (handler != nullptr) {
                    handler();
                    return true;
                }
            }
        }
        return false;
    }

private:
    [[nodiscard]] const Resource* find_resource(uint16_t obj_id, uint16_t inst_id, uint16_t res_id) const noexcept {
        for (const auto& obj : registry_) {
            if (obj.id != obj_id) continue;
            for (const auto& inst : obj.instances) {
                if (inst.id != inst_id) continue;
                for (const auto& res : inst.resources) {
                    if (res.id == res_id) return &res;
                }
            }
        }
        return nullptr;
    }

    std::span<Object> registry_;
};

} // namespace lwm2m
