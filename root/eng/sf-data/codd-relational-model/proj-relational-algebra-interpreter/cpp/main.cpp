#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <ranges>
#include <stdexcept>

struct Tuple {
    std::vector<std::string> values;

    auto operator<=>(const Tuple&) const = default;
};

class Relation {
public:
    std::string name;
    std::vector<std::string> schema;
    std::vector<Tuple> tuples;

    Relation(std::string name, std::vector<std::string> schema)
        : name(std::move(name)), schema(std::move(schema)) {}

    void add_tuple(Tuple t) {
        if (t.values.size() != schema.size()) {
            throw std::invalid_argument("Розмірність кортежу не відповідає схемі");
        }
        if (std::find(tuples.begin(), tuples.end(), t) == tuples.end()) {
            tuples.push_back(std::move(t));
        }
    }

    [[nodiscard]] int find_attr(const std::string& attr) const {
        for (size_t i = 0; i < schema.size(); ++i) {
            if (schema[i] == attr) return static_cast<int>(i);
        }
        return -1;
    }

    // Оператор Селекції σ_{attr = val}(R)
    [[nodiscard]] Relation select(const std::string& attr, const std::string& target_val) const {
        Relation res("sigma_" + attr + "=" + target_val + "(" + name + ")", schema);
        int idx = find_attr(attr);
        if (idx < 0) return res;

        for (const auto& t : tuples) {
            if (t.values[idx] == target_val) {
                res.add_tuple(t);
            }
        }
        return res;
    }

    // Оператор Проекції π_{attrs}(R)
    [[nodiscard]] Relation project(const std::vector<std::string>& proj_attrs) const {
        Relation res("pi(" + name + ")", proj_attrs);
        std::vector<int> map_idx;
        for (const auto& attr : proj_attrs) {
            map_idx.push_back(find_attr(attr));
        }

        for (const auto& t : tuples) {
            Tuple proj_tuple;
            for (int idx : map_idx) {
                proj_tuple.values.push_back(idx >= 0 ? t.values[idx] : "NULL");
            }
            res.add_tuple(proj_tuple);
        }
        return res;
    }

    // Оператор Природного З'єднання R ⋈ S
    [[nodiscard]] Relation natural_join(const Relation& other) const {
        std::vector<std::string> out_schema = schema;
        int join_idx_this = -1;
        int join_idx_other = -1;

        for (size_t i = 0; i < schema.size(); ++i) {
            int idx = other.find_attr(schema[i]);
            if (idx >= 0) {
                join_idx_this = static_cast<int>(i);
                join_idx_other = idx;
                break;
            }
        }

        for (size_t j = 0; j < other.schema.size(); ++j) {
            if (static_cast<int>(j) != join_idx_other) {
                out_schema.push_back(other.schema[j]);
            }
        }

        Relation res("(" + name + " JOIN " + other.name + ")", out_schema);

        for (const auto& t1 : tuples) {
            for (const auto& t2 : other.tuples) {
                bool match = (join_idx_this < 0) || 
                             (t1.values[join_idx_this] == t2.values[join_idx_other]);
                if (match) {
                    Tuple merged = t1;
                    for (size_t k = 0; k < t2.values.size(); ++k) {
                        if (static_cast<int>(k) != join_idx_other) {
                            merged.values.push_back(t2.values[k]);
                        }
                    }
                    res.add_tuple(merged);
                }
            }
        }
        return res;
    }

    void print() const {
        std::cout << "=== Відношення: " << name << " ===\n| ";
        for (const auto& col : schema) std::cout << col << "\t| ";
        std::cout << "\n----------------------------------------\n";
        for (const auto& t : tuples) {
            std::cout << "| ";
            for (const auto& val : t.values) std::cout << val << "\t| ";
            std::cout << "\n";
        }
        std::cout << "\n";
    }
};

int main() {
    Relation users("Users", {"ID", "Name", "City"});
    users.add_tuple({{"101", "Аліса", "Київ"}});
    users.add_tuple({{"102", "Боб", "Львів"}});
    users.add_tuple({{"103", "Єва", "Київ"}});

    Relation orders("Orders", {"OrderID", "ID", "Amount"});
    orders.add_tuple({{"5001", "101", "250.0"}});
    orders.add_tuple({{"5002", "101", "120.0"}});
    orders.add_tuple({{"5003", "102", "890.0"}});

    users.print();
    orders.print();

    // 1. Селекція σ_{City = 'Київ'}
    Relation kyiv = users.select("City", "Київ");
    kyiv.print();

    // 2. Природне з'єднання Users ⋈ Orders
    Relation joined = users.natural_join(orders);
    joined.print();

    // 3. Проекція π_{Name, Amount}
    Relation final_res = joined.project({"Name", "Amount"});
    final_res.print();

    return 0;
}
