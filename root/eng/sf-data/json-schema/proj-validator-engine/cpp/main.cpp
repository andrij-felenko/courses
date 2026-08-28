#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <optional>
#include <variant>
#include <span>

enum class JsonType {
    Null,
    Boolean,
    Integer,
    Number,
    String,
    Object,
    Array
};

struct JsonValue;

using JsonObject = std::unordered_map<std::string, std::shared_ptr<JsonValue>>;
using JsonArray = std::vector<std::shared_ptr<JsonValue>>;

struct JsonValue {
    JsonType type;
    std::variant<std::monostate, bool, int64_t, double, std::string, JsonObject, JsonArray> data;

    static std::shared_ptr<JsonValue> make_int(int64_t v) {
        auto val = std::make_shared<JsonValue>();
        val->type = JsonType::Integer;
        val->data = v;
        return val;
    }

    static std::shared_ptr<JsonValue> make_num(double v) {
        auto val = std::make_shared<JsonValue>();
        val->type = JsonType::Number;
        val->data = v;
        return val;
    }

    static std::shared_ptr<JsonValue> make_obj(JsonObject v) {
        auto val = std::make_shared<JsonValue>();
        val->type = JsonType::Object;
        val->data = std::move(v);
        return val;
    }
};

struct ValidationError {
    std::string instance_location;
    std::string keyword_location;
    std::string message;
};

class SchemaNode {
public:
    std::optional<JsonType> expected_type;
    std::optional<double> minimum;
    std::optional<double> maximum;
    std::vector<std::string> required_fields;
    std::unordered_map<std::string, std::shared_ptr<SchemaNode>> properties;
    std::shared_ptr<SchemaNode> ref_target;

    [[nodiscard]] bool validate(const JsonValue& instance,
                                std::string_view path,
                                std::vector<ValidationError>& errors) const {
        if (ref_target) {
            return ref_target->validate(instance, path, errors);
        }

        if (expected_type.has_value()) {
            if (*expected_type == JsonType::Number) {
                if (instance.type != JsonType::Number && instance.type != JsonType::Integer) {
                    errors.push_back({std::string(path), "/type", "Expected numeric type"});
                    return false;
                }
            } else if (instance.type != *expected_type) {
                errors.push_back({std::string(path), "/type", "Type assertion mismatch"});
                return false;
            }
        }

        if (instance.type == JsonType::Number || instance.type == JsonType::Integer) {
            double val = (instance.type == JsonType::Integer) 
                ? static_cast<double>(std::get<int64_t>(instance.data))
                : std::get<double>(instance.data);

            if (minimum.has_value() && val < *minimum) {
                errors.push_back({std::string(path), "/minimum", "Value violates minimum constraint"});
                return false;
            }
            if (maximum.has_value() && val > *maximum) {
                errors.push_back({std::string(path), "/maximum", "Value violates maximum constraint"});
                return false;
            }
        }

        if (instance.type == JsonType::Object) {
            const auto& obj = std::get<JsonObject>(instance.data);

            for (const auto& req : required_fields) {
                if (!obj.contains(req)) {
                    std::string field_path = std::string(path) + "/" + req;
                    errors.push_back({field_path, "/required", "Required property is missing"});
                    return false;
                }
            }

            for (const auto& [key, val_ptr] : obj) {
                if (auto it = properties.find(key); it != properties.end()) {
                    std::string subpath = std::string(path) + "/" + key;
                    if (!it->second->validate(*val_ptr, subpath, errors)) {
                        return false;
                    }
                }
            }
        }

        return true;
    }
};

int main() {
    auto coord_schema = std::make_shared<SchemaNode>();
    coord_schema->expected_type = JsonType::Object;
    coord_schema->required_fields = {"lat", "lon"};
    
    auto lat_prop = std::make_shared<SchemaNode>();
    lat_prop->expected_type = JsonType::Number;
    lat_prop->minimum = -90.0;
    lat_prop->maximum = 90.0;
    
    auto lon_prop = std::make_shared<SchemaNode>();
    lon_prop->expected_type = JsonType::Number;
    lon_prop->minimum = -180.0;
    lon_prop->maximum = 180.0;

    coord_schema->properties["lat"] = lat_prop;
    coord_schema->properties["lon"] = lon_prop;

    auto root_schema = std::make_shared<SchemaNode>();
    root_schema->expected_type = JsonType::Object;
    root_schema->required_fields = {"userId", "amount", "location"};

    auto user_id_prop = std::make_shared<SchemaNode>();
    user_id_prop->expected_type = JsonType::Integer;
    user_id_prop->minimum = 1.0;

    auto amount_prop = std::make_shared<SchemaNode>();
    amount_prop->expected_type = JsonType::Number;
    amount_prop->minimum = 0.01;

    root_schema->properties["userId"] = user_id_prop;
    root_schema->properties["amount"] = amount_prop;
    root_schema->properties["location"] = coord_schema;

    JsonObject loc_data;
    loc_data["lat"] = JsonValue::make_num(50.4501);
    loc_data["lon"] = JsonValue::make_num(30.5234);

    JsonObject order_data;
    order_data["userId"] = JsonValue::make_int(42);
    order_data["amount"] = JsonValue::make_num(199.99);
    order_data["location"] = JsonValue::make_obj(std::move(loc_data));

    auto document = JsonValue::make_obj(std::move(order_data));

    std::vector<ValidationError> errors;
    bool is_valid = root_schema->validate(*document, "", errors);

    if (is_valid) {
        std::cout << "Validation successful: JSON document conforms to schema.\n";
    } else {
        std::cout << "Validation failed:\n";
        for (const auto& err : errors) {
            std::cout << " - [" << err.instance_location << "] (Rule: " 
                      << err.keyword_location << "): " << err.message << "\n";
        }
    }

    return 0;
}
