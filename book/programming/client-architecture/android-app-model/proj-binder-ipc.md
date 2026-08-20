# ⚙️ Міжпроцесна взаємодія через Binder і перевірка прав

Коли два мобільні процеси з різними ідентифікаторами користувача (`UID`) повинні обмінюватися конфіденційними даними або делегувати виконання операцій, класичні сокети чи спільні файли створюють високі накладні витрати й ризики безпеки. Потрібен механізм, який гарантує прямий RPC-виклик (Remote Procedure Call) із мінімальним копіюванням байтів і апаратною перевіркою справжності клієнта на рівні ядра ОС.

В Android цей контракт реалізується через інтерфейс опису мови AIDL (Android Interface Definition Language), компільований у клієнтський проксі (`BinderProxy`) та серверний заглушку-обробник (`Binder Stub`). Під капотом кожна передача структури транслюється в послідовність записів у низькорівневий буфер `Parcel`, який драйвер ядра `/dev/binder` переносить між адресними просторами за одну операцію копіювання пам'яті.

## Постановка задачі та протокол взаємодії

Розробити захищений ізольований сервіс керування сховищем ключів, що працює в окремому фоновому процесі `:secure_vault` з власним `UID`. Сервіс повинен:
1. Оголошувати RPC-методи для збереження та читання зашифрованих секретів із гарантією цілісності.
2. Перевіряти наявність у клієнта спеціального дозволу `com.example.vault.permission.ACCESS_VAULT` з рівнем захисту `signature`.
3. Валідувати справжній `UID` процесу, що ініціював виклик, безпосередньо через системний виклик ядра `Binder.getCallingUid()`.
4. Обробляти випадки розриву зв'язку (смерть віддаленого процесу) через реєстрацію `IBinder.DeathRecipient`.

Архітектура взаємодії спирається на три рівні абстракції:
- **Шар застосунку:** типізований інтерфейс Kotlin/C++, що приховує деталі маршалінгу.
- **Шар фреймворку (libbinder / libbinder_ndk):** класи `Parcel`, `IBinder` та згенеровані Stub-обробники транзакцій.
- **Шар ядра:** драйвер `/dev/binder`, який маршрутизує транзакцію за числовим кодом методу (`transaction code`) та автоматично інжектує перевірені ідентифікатори `calling_uid` і `calling_pid` у контекст виклику.

## Інтерфейс AIDL та структура даних

Оголосимо файл контракту `ISecureVault.aidl`. Компілятор AIDL автоматично згенерує інтерфейс Java/Kotlin із внутрішнім абстрактним класом `Stub`. Під час виклику клієнтський проксі серіалізує параметри у бінарний контейнер `Parcel`, додає заголовок інтерфейсу `interface token` (для захисту від підміни протоколу) та виконує системний виклик `ioctl` із командою `BINDER_WRITE_READ`.

```aidl
// ISecureVault.aidl
package com.example.vault;

interface ISecureVault {
    void storeSecret(in String key, in byte[] payload);
    byte[] retrieveSecret(in String key);
    int getCallerProcessUid();
}
```

## Реалізація захищеного сервісу та перевірка виклику

Сервіс перехоплює виклики, витягує `callingUid` з контексту ядрового драйвера `/dev/binder` та звіряє цифровий підпис клієнтського пакета з власним підписом за допомогою `PackageManager`. Оскільки ядро Linux гарантує незмінність `callingUid`, клієнтський процес не має жодної технічної можливості видати себе за інший застосунок.

Важливо розуміти поведінку методу `Binder.getCallingUid()`: він повертає ідентифікатор викликача лише **під час обробки вхідної транзакції Binder**. Якщо викликати цей метод поза контекстом транзакції (наприклад, у головному потоці сервісу після завершення виклику), він поверне власний `UID` поточного процесу.

:::tabs
```kotlin
package com.example.vault

import android.app.Service
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Binder
import android.os.IBinder
import android.os.Process
import android.os.RemoteException
import java.util.concurrent.ConcurrentHashMap

class SecureVaultService : Service() {

    private val storage = ConcurrentHashMap<String, ByteArray>()

    private val binder = object : ISecureVault.Stub() {
        override fun storeSecret(key: String, payload: ByteArray) {
            enforceSignaturePermission()
            if (payload.size > 256 * 1024) {
                throw IllegalArgumentException("Розмір корисного навантаження перевищує 256 КБ")
            }
            storage[key] = payload
        }

        override fun retrieveSecret(key: String): ByteArray {
            enforceSignaturePermission()
            return storage[key] ?: ByteArray(0)
        }

        override fun getCallerProcessUid(): Int {
            return Binder.getCallingUid()
        }

        private fun enforceSignaturePermission() {
            val callingUid = Binder.getCallingUid()
            val callingPid = Binder.getCallingPid()

            // Якщо виклик локальний (у межах власного процесу), перевірку пропускаємо
            if (callingUid == Process.myUid()) {
                return
            }

            // 1. Перевірка статичного або динамічного дозволу
            val permCheck = checkCallingOrSelfPermission(
                "com.example.vault.permission.ACCESS_VAULT"
            )
            if (permCheck != PackageManager.PERMISSION_GRANTED) {
                throw SecurityException(
                    "Процес UID $callingUid (PID $callingPid) не має дозволу ACCESS_VAULT"
                )
            }

            // 2. Додаткова строга верифікація збігу сертифіката підпису (signature protection)
            val match = packageManager.checkSignatures(callingUid, Process.myUid())
            if (match != PackageManager.SIGNATURE_MATCH) {
                throw SecurityException(
                    "Підпис клієнтського застосунку (UID $callingUid) не збігається з підписом сховища"
                )
            }
        }
    }

    override fun onBind(intent: Intent?): IBinder {
        return binder
    }
}
```
```cpp
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
```
:::

## Декларація дозволу та сервісу в маніфесті

Щоб сторонні неавторизовані програми не могли навіть підключитися до сервісу, ми захищаємо його тегом `<permission>` із атрибутом `protectionLevel="signature"`. При спробі будь-якого стороннього застосунку, підписаного іншим сертифікатом розробника, виконати `bindService()`, системна служба `ActivityTaskManager` автоматично заблокує спробу зв'язування ще на етапі аналізу маніфесту без запуску нашого процесу.

Атрибут `android:process=":secure_vault"` повідомляє операційній системі, що цей компонент повинен виконуватися у власному ізольованому Linux-процесі. Двокрапка на початку назви процесу вказує, що процес є приватним для нашого пакета, проте його `UID` та пам'ять ізольовані від головного інтерфейсного процесу застосунку.

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.vault">

    <!-- Оголошення власного дозволу, доступного лише застосункам з тим самим ключем підпису -->
    <permission
        android:name="com.example.vault.permission.ACCESS_VAULT"
        android:protectionLevel="signature" />

    <application>
        <service
            android:name=".SecureVaultService"
            android:process=":secure_vault"
            android:exported="true"
            android:permission="com.example.vault.permission.ACCESS_VAULT">
            <intent-filter>
                <action android:name="com.example.vault.ACTION_BIND_VAULT" />
            </intent-filter>
        </service>
    </application>
</manifest>
```

## Клієнтське підключення та обробка розриву зв'язку

Клієнт повинен зв'язатися з віддаленим сервісом через `bindService` та обов'язково зареєструвати обробник смерті процесу `IBinder.DeathRecipient`, оскільки ядро ОС може знищити процес `:secure_vault` у будь-яку мить через нестачу пам'яті за правилами Low Memory Killer.

Коли процес-сервер раптово завершує роботу, клієнтський об'єкт `BinderProxy` переходить у недійсний стан. Будь-який наступний виклик методу кине виключення `DeadObjectException` (підклас `RemoteException`). Реєстрація `DeathRecipient` дає змогу дізнатися про падіння сервера асинхронно, очистити локальні посилання та ініціювати процедуру повторного підключення без падіння клієнтського інтерфейсу.

:::tabs
```kotlin
package com.example.client

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.IBinder
import android.os.RemoteException
import android.util.Log
import com.example.vault.ISecureVault

class VaultClient(private val context: Context) {

    private var vaultService: ISecureVault? = null
    private var isBound = false

    private val deathRecipient = IBinder.DeathRecipient {
        Log.e("VaultClient", "Віддалений процес сервісу вбито ядром (Process Death)!")
        vaultService = null
        isBound = false
        // Логіка повторного автоматичного підключення за потреби
    }

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            try {
                service?.linkToDeath(deathRecipient, 0)
                vaultService = ISecureVault.Stub.asInterface(service)
                isBound = true
                Log.i("VaultClient", "Успішно з'єднано з віддаленим сервісом")
            } catch (e: RemoteException) {
                Log.e("VaultClient", "Не вдалося прив'язати DeathRecipient", e)
            }
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            // Викликається при неочікуваному розриві зв'язку
            vaultService = null
            isBound = false
        }
    }

    fun connect() {
        val intent = Intent("com.example.vault.ACTION_BIND_VAULT").apply {
            setPackage("com.example.vault") // Явний намір для безпеки зв'язування
        }
        context.bindService(intent, connection, Context.BIND_AUTO_CREATE)
    }

    fun save(key: String, secretData: ByteArray) {
        val service = vaultService ?: throw IllegalStateException("Сервіс не підключено")
        try {
            service.storeSecret(key, secretData)
        } catch (e: RemoteException) {
            // Перехоплення помилки падіння віддаленого Binder-каналу
            Log.e("VaultClient", "Помилка IPC-транзакції: віддалений сервіс розірвав канал", e)
        }
    }

    fun disconnect() {
        if (isBound) {
            vaultService?.asBinder()?.unlinkToDeath(deathRecipient, 0)
            context.unbindService(connection)
            isBound = false
        }
    }
}
```
```cpp
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
```
:::

## Архітектурні пастки та граничні випадки

Практична робота з міжпроцесними викликами Binder вимагає врахування низки системних обмежень ядра:

1. **Ліміт пулу пам'яті транзакцій Binder (1 МБ):** Буфер відображення сторінок пам'яті Binder є спільним для всіх одночасних вхідних викликів у межах процесу. Якщо кілька потоків одночасно передають дані через `storeSecret()`, сумарний обсяг не може перевищувати встановлений поріг пам'яті (зазвичай від 512 КБ до 1 МБ залежно від версії ОС). Спроба передати велике бінарне зображення або масив призведе до викидання невідновного системного виключення `android.os.TransactionTooLargeException`. Для передачі великих масивів даних слід використовувати механізм `SharedMemory` або передавати файловий дескриптор `ParcelFileDescriptor` через anonymous pipe.
2. **Блокування потоку інтерфейсу клієнта:** Виклик будь-якого методу згенерованого AIDL-інтерфейсу є **синхронним і блокуючим** за замовчуванням. Якщо віддалений процес виконує операцію дискового вводу-виводу або зайнятий тривалим обчисленням, потік клієнта заблокується на системному виклику `ioctl(binderFd, BINDER_WRITE_READ)`. Викликати методи Binder-сервісу з головного UI-потоку суворо заборонено; слід делегувати виклики у фонові корутини або диспетчер пулу потоків.
3. **Взаємне блокування (Deadlock) при зворотних викликах:** Якщо сервіс A синхронно викликає метод сервісу B, а сервіс B під час цього виклику робить синхронний зворотний виклик у сервіс A, потоки заблокують один одного, якщо в пулі Binder-потоків сервісу A закінчаться доступні виконавці (за замовчуванням пул обмежений 16 потоками на процес). Для зворотного зв'язку слід використовувати неблокуючі односторонні методи з ключовим словом `oneway` у визначенні AIDL. Односторонній виклик не повертає значення, не чекає відповіді віддаленого процесу та не передає виключень клієнту.
4. **Очищення реєстрації DeathRecipient:** Невиконання `unlinkToDeath` під час штатного відключення клієнта призводить до витоку пам'яті на рівні ядра, оскільки драйвер `/dev/binder` продовжує утримувати структуру зворотного сповіщення для дескриптора мертвого об'єкта.

