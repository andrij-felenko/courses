#include <android/binder_ibinder.h>
#include <android/binder_auto_utils.h>
#include <iostream>
#include <memory>

// Обробник раптового знищення зв'язку на боці нативного клієнта
void onBinderDied(void* cookie) {
    std::cerr << "[NativeClient] Серверний процес раптово завершився (Binder Died)" << std::endl;
}

class NativeVaultClient {
private:
    ndk::SpAIBinder mBinder;
    ndk::ScopedAIBinder_DeathRecipient mDeathRecipient;

public:
    NativeVaultClient() 
        : mDeathRecipient(AIBinder_DeathRecipient_new(onBinderDied)) {}

    void attachBinder(AIBinder* rawBinder) {
        mBinder = ndk::SpAIBinder(rawBinder);
        if (mBinder.get() != nullptr) {
            // Реєстрація death recipient для безпеки життєвого циклу
            AIBinder_linkToDeath(mBinder.get(), mDeathRecipient.get(), this);
        }
    }

    void detach() {
        if (mBinder.get() != nullptr) {
            AIBinder_unlinkToDeath(mBinder.get(), mDeathRecipient.get(), this);
            mBinder = nullptr;
        }
    }
};
