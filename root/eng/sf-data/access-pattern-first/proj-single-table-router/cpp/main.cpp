#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <map>
#include <optional>
#include <memory>
#include <sstream>

namespace single_table {

struct Item {
    std::string pk;
    std::string sk;
    std::string gsi1pk;
    std::string gsi1sk;
    std::string entity_type;
    std::string payload;
};

class SingleTableStore {
public:
    void put_item(Item item) {
        std::string pk = item.pk;
        std::string sk = item.sk;
        std::string gsi1pk = item.gsi1pk;

        // Збереження в основну таблицю
        table_[pk][sk] = item;

        // Збереження в вторинний індекс (GSI1)
        if (!gsi1pk.empty()) {
            gsi1_index_[gsi1pk][item.gsi1sk] = item;
        }
    }

    std::optional<Item> get_item(const std::string& pk, const std::string& sk) const {
        auto it_pk = table_.find(pk);
        if (it_pk != table_.end()) {
            auto it_sk = it_pk->second.find(sk);
            if (it_sk != it_pk->second.end()) {
                return it_sk->second;
            }
        }
        return std::nullopt;
    }

    // Вибірка всіх елементів колекції або за префіксом begins_with
    std::vector<Item> query(const std::string& pk, const std::string& sk_prefix = "") const {
        std::vector<Item> results;
        auto it_pk = table_.find(pk);
        if (it_pk == table_.end()) {
            return results;
        }

        for (const auto& [sk, item] : it_pk->second) {
            if (sk_prefix.empty() || sk.rfind(sk_prefix, 0) == 0) {
                results.push_back(item);
            }
        }
        return results;
    }

    // Вибірка через GSI1
    std::vector<Item> query_gsi1(const std::string& gsi1pk, const std::string& gsi1sk_prefix = "") const {
        std::vector<Item> results;
        auto it_gsi = gsi1_index_.find(gsi1pk);
        if (it_gsi == gsi1_index_.end()) {
            return results;
        }

        for (const auto& [gsi1sk, item] : it_gsi->second) {
            if (gsi1sk_prefix.empty() || gsi1sk.rfind(gsi1sk_prefix, 0) == 0) {
                results.push_back(item);
            }
        }
        return results;
    }

    bool remove(const std::string& pk, const std::string& sk) {
        auto it_pk = table_.find(pk);
        if (it_pk == table_.end()) return false;

        auto it_sk = it_pk->second.find(sk);
        if (it_sk == it_pk->second.end()) return false;

        std::string gsi1pk = it_sk->second.gsi1pk;
        std::string gsi1sk = it_sk->second.gsi1sk;

        it_pk->second.erase(it_sk);

        if (!gsi1pk.empty()) {
            auto it_gsi = gsi1_index_.find(gsi1pk);
            if (it_gsi != gsi1_index_.end()) {
                it_gsi->second.erase(gsi1sk);
            }
        }

        return true;
    }

    // Пакетне видалення всієї колекції елементів за Partition Key
    size_t delete_collection(const std::string& pk) {
        auto it_pk = table_.find(pk);
        if (it_pk == table_.end()) return 0;

        size_t deleted_count = 0;
        for (const auto& [sk, item] : it_pk->second) {
            if (!item.gsi1pk.empty()) {
                gsi1_index_[item.gsi1pk].erase(item.gsi1sk);
            }
            deleted_count++;
        }

        table_.erase(it_pk);
        return deleted_count;
    }

private:
    std::unordered_map<std::string, std::map<std::string, Item>> table_;
    std::unordered_map<std::string, std::map<std::string, Item>> gsi1_index_;
};

} // namespace single_table

int main() {
    using namespace single_table;
    SingleTableStore store;

    // Вставка сутностей
    store.put_item({"USER#42", "#METADATA", "", "", "User", "{\"username\": \"john_doe\"}"});
    store.put_item({"USER#42", "ORDER#2024-05-10#99", "ORDER#99", "USER#42", "Order", "{\"amount\": 450}"});
    store.put_item({"USER#42", "ORDER#2024-05-11#100", "ORDER#100", "USER#42", "Order", "{\"amount\": 890}"});

    // 1. Отримання всіх замовлень за префіксом
    auto orders = store.query("USER#42", "ORDER#");
    std::cout << "Orders found: " << orders.size() << std::endl;

    // 2. Отримання інформації про замовлення за його ID
    auto order_ref = store.query_gsi1("ORDER#99");
    if (!order_ref.empty()) {
        std::cout << "Order belongs to: " << order_ref[0].pk << std::endl;
    }

    return 0;
}
