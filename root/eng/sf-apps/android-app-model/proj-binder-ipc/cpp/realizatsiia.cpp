#include <android/binder_ibinder.h>
#include <android/binder_auto_utils.h>
#include <unistd.h>
#include <map>
#include <string>
#include <vector>
#include <mutex>
#include <stdexcept>

// Нативна реалізація Binder-сервісу з використанням NDK libbinder_ndk
class SecureVaultNativeService {
private:
    std::mutex mMutex;
    std::map<std::string, std::vector<uint8_t>> mStorage;

    void enforceCallerSecurity() {
        uid_t callingUid = AIBinder_getCallingUid();
        pid_t callingPid = AIBinder_getCallingPid();

        // Перевірка, що виклик не йде від невідомого або скомпрометованого UID
        if (callingUid != getuid()) {
            // На рівні C++ NDK перевіряємо валідність UID перед обробкою буфера
            if (callingUid < 10000) { // Системні чи некоректні UID
                throw std::runtime_error("Недозволений системний UID або відсутність прав доступу");
            }
        }
    }

public:
    bool storeSecret(const std::string& key, const std::vector<uint8_t>& data) {
        enforceCallerSecurity();
        if (data.size() > 256 * 1024) {
            return false; // Запобігання переповненню буфера транзакції Binder
        }
        std::lock_guard<std::mutex> lock(mMutex);
        mStorage[key] = data;
        return true;
    }

    std::vector<uint8_t> retrieveSecret(const std::string& key) {
        enforceCallerSecurity();
        std::lock_guard<std::mutex> lock(mMutex);
        auto it = mStorage.find(key);
        if (it != mStorage.end()) {
            return it->second;
        }
        return {};
    }
};
