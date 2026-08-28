// --- adapter_a.cpp: єдине місце, що знає SDK вендора A ---
#include <vendora/client.h>   // тип вендора живе ЛИШЕ в цьому файлі

class VendorAStore : public ObjectStore {
    vendora::Client cli_;
public:
    explicit VendorAStore(const std::string& bucket)
        : cli_(bucket) {}

    void put(const std::string& key, const std::string& bytes) override {
        vendora::Status s = cli_.write(key, bytes.data(), bytes.size());
        if (s != vendora::OK)
            throw StoreError("vendorA put: " + vendora::str(s));
    }

    std::optional<std::string> get(const std::string& key) override {
        vendora::Buffer buf;
        vendora::Status s = cli_.read(key, &buf);
        if (s == vendora::NOT_FOUND) return std::nullopt;   // не помилка!
        if (s != vendora::OK)
            throw StoreError("vendorA get: " + vendora::str(s));
        return std::string(buf.data(), buf.size());
    }

    std::vector<std::string> list(const std::string& prefix) override {
        std::vector<std::string> out;
        for (auto& obj : cli_.enumerate(prefix))   // SDK сам гортає сторінки
            out.push_back(obj.key());
        return out;
    }
};
