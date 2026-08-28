// --- adapter_b.cpp: єдине місце, що знає SDK вендора B ---
#include <vendorb/blob.hpp>   // тип вендора живе ЛИШЕ в цьому файлі

class VendorBStore : public ObjectStore {
    vendorb::BlobService svc_;
public:
    explicit VendorBStore(const std::string& container)
        : svc_(vendorb::connect(container)) {}

    void put(const std::string& key, const std::string& bytes) override {
        try {
            svc_.upload(key, bytes);              // кидає при збої
        } catch (const vendorb::Exception& e) {
            throw StoreError(std::string("vendorB put: ") + e.what());
        }
    }

    std::optional<std::string> get(const std::string& key) override {
        try {
            vendorb::Blob b = svc_.download(key);
            return b.as_string();
        } catch (const vendorb::NotFound&) {
            return std::nullopt;                 // приводимо до нашого правила
        } catch (const vendorb::Exception& e) {
            throw StoreError(std::string("vendorB get: ") + e.what());
        }
    }

    std::vector<std::string> list(const std::string& prefix) override {
        std::vector<std::string> out;
        for (auto& name : svc_.list_blobs(prefix))
            out.push_back(name);
        return out;
    }
};
