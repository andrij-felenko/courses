#include <iostream>
#include <string>
#include <sstream>
#include <vector>

class KeyBuilder {
public:
    static std::string make_user_pk(int user_id) {
        return "USER#" + std::to_string(user_id);
    }

    static std::string make_order_sk(const std::string& date, int order_id) {
        std::ostringstream ss;
        ss << "ORDER#" << date << "#" << order_id;
        return ss.str();
    }

    static bool begins_with(const std::string& key, const std::string& prefix) {
        return key.rfind(prefix, 0) == 0;
    }
};
