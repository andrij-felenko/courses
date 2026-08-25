# ⚙️ Реалізація COM-об'єкта та фабрики класів з нуля: C та ідіоматичний C++

Щоб досконало розібратися, як компонентна модель COM функціонує на рівні машинних інструкцій та бінарного макета пам'яті без використання високорівневих компіляторних розширень, бібліотеки ATL чи фреймворків, розглянемо повну реалізацію внутрішньопроцесного (In-Process) COM-компонента та клієнта. Ми побудуємо інтерфейс обчислювального вузла `ICalculator`, реалізуємо канонічні правила життєвого циклу `IUnknown`, створимо фабрику класів `IClassFactory` та дослідимо точний механізм завантаження DLL операційною системою.

Усі лістинги наведено паралельно двома мовами: мовою **C**, де віртуальні таблиці, структури інтерфейсів та списки вказівників конструюються вручну, та сучасною **C++**, де використовується абстрактне множинне успадкування, компіляторні атрибути `__declspec(novtable)`, атомарні операції та RAII-обгортки `Microsoft::WRL::ComPtr`.

## 1. Бінарний контракт: vtable, вирівнювання та унікальні ідентифікатори (GUID)

Кожен COM-інтерфейс є строго фіксованою структурою у пам'яті. Першим полем структури є вказівник на таблицю адрес функцій (`vtable`), а перші три слоти будь-якої таблиці завжди займають методи інтерфейсу `IUnknown`: `QueryInterface` (індекс 0), `AddRef` (індекс 1) та `Release` (індекс 2).

Методи використовують угоду про виклики `__stdcall` (`STDMETHODCALLTYPE`), за якої аргументи передаються через стек справа наліво, а очищення стека покладається на викликану функцію (callee). На архітектурі x86-64 `__stdcall` автоматично узгоджується зі стандартною угодою Microsoft x64 ABI (перші 4 аргументи в регістрах `RCX`, `RDX`, `R8`, `R9`).

Унікальність інтерфейсу та класу гарантується 128-бітними глобальними ідентифікаторами (GUID). `CLSID_Calculator` ідентифікує конкретну реалізацію калькулятора, а `IID_ICalculator` — незмінний контракт його методів.

:::tabs
```c
#define COBJMACROS
#include <windows.h>
#include <unknwn.h>
#include <stdio.h>

/* CLSID_Calculator: {E4A28B10-53D2-4A73-98D1-9B5A2D6E4310} */
static const GUID CLSID_Calculator = {
    0xe4a28b10, 0x53d2, 0x4a73,
    { 0x98, 0xd1, 0x9b, 0x5a, 0x2d, 0x6e, 0x43, 0x10 }
};

/* IID_ICalculator: {A1B2C3D4-E5F6-4A5B-8C7D-9E0F1A2B3C4D} */
static const GUID IID_ICalculator = {
    0xa1b2c3d4, 0xe5f6, 0x4a5b,
    { 0x8c, 0x7d, 0x9e, 0x0f, 0x1a, 0x2b, 0x3c, 0x4d }
};

/* Бінарна vtable інтерфейсу ICalculator у C */
typedef struct ICalculatorVtbl {
    /* 1. Обов'язкова секція IUnknown */
    HRESULT (STDMETHODCALLTYPE *QueryInterface)(void *This, REFIID riid, void **ppvObject);
    ULONG   (STDMETHODCALLTYPE *AddRef)(void *This);
    ULONG   (STDMETHODCALLTYPE *Release)(void *This);

    /* 2. Специфічні методи ICalculator */
    HRESULT (STDMETHODCALLTYPE *Add)(void *This, double a, double b, double *result);
    HRESULT (STDMETHODCALLTYPE *Multiply)(void *This, double a, double b, double *result);
} ICalculatorVtbl;

/* Інтерфейсна структура для клієнта: вказівник на таблицю vtable */
typedef struct ICalculator {
    const ICalculatorVtbl *lpVtbl;
} ICalculator;
```
```cpp
#include <windows.h>
#include <unknwn.h>
#include <wrl/client.h>
#include <iostream>
#include <atomic>

/* CLSID_Calculator: {E4A28B10-53D2-4A73-98D1-9B5A2D6E4310} */
inline constexpr GUID CLSID_Calculator = {
    0xe4a28b10, 0x53d2, 0x4a73,
    { 0x98, 0xd1, 0x9b, 0x5a, 0x2d, 0x6e, 0x43, 0x10 }
};

/* IID_ICalculator: {A1B2C3D4-E5F6-4A5B-8C7D-9E0F1A2B3C4D} */
inline constexpr GUID IID_ICalculator = {
    0xa1b2c3d4, 0xe5f6, 0x4a5b,
    { 0x8c, 0x7d, 0x9e, 0x0f, 0x1a, 0x2b, 0x3c, 0x4d }
};

/* Чистий абстрактний інтерфейс у C++ */
struct __declspec(novtable) ICalculator : public IUnknown {
    virtual HRESULT STDMETHODCALLTYPE Add(double a, double b, double *result) = 0;
    virtual HRESULT STDMETHODCALLTYPE Multiply(double a, double b, double *result) = 0;
};
```
:::

Зверніть увагу на атрибут `__declspec(novtable)` у коді C++: він інструктує компілятор не генерувати проміжну віртуальну таблицю для абстрактного інтерфейсного базового класу, оскільки цей клас не має власної реалізації. Це дозволяє уникнути непотрібного коду в бінарному файлі.

## 2. Реалізація компонента та інваріантів IUnknown

Реалізація компонента інкапсулює внутрішній стан: лічильник посилань `m_refCount` та власні змінні. При цьому клієнт не має прямого доступу до жодного з полів об'єкта, окрім віртуальної таблиці.

Під час написання `QueryInterface` необхідно неухильно дотримуватися чотирьох фундаментальних аксіом COM:
1. **Рефлексивність:** Запит інтерфейсу від самого себе (`pCalc->QI(IID_ICalculator)`) завжди завершується успіхом зі статусом `S_OK`.
2. **Симетричність:** Якщо через інтерфейс `A` можна отримати інтерфейс `B`, то через `B` гарантовано можна повернутися до `A`.
3. **Транзитивність:** Якщо з `A` доступний `B`, а з `B` доступний `C`, то з `A` можна напряму отримати `C`.
4. **Ідентичність об'єкта (Object Identity):** Запит `IID_IUnknown` від будь-якого інтерфейсу екземпляра зобов'язаний повертати однакове числове значення адреси покажчика.

Кожен успішний виклик `QueryInterface` збільшує лічильник посилань через `AddRef()`. Коли клієнт закінчує роботу з інтерфейсом, він викликає `Release()`. Щойно лічильник падає до нуля, об'єкт викликає власний деструктор і звільняє пам'ять.

:::tabs
```c
typedef struct CalculatorImpl {
    const ICalculatorVtbl *lpVtbl;
    LONG m_refCount;
} CalculatorImpl;

static HRESULT STDMETHODCALLTYPE Calc_QueryInterface(void *This, REFIID riid, void **ppvObject) {
    CalculatorImpl *pThis = (CalculatorImpl*)This;
    if (!ppvObject) return E_POINTER;

    /* Перевірка ідентичності та підтримуваних інтерфейсів */
    if (IsEqualGUID(riid, &IID_IUnknown) || IsEqualGUID(riid, &IID_ICalculator)) {
        *ppvObject = pThis;
        pThis->lpVtbl->AddRef(This);
        return S_OK;
    }

    *ppvObject = NULL;
    return E_NOINTERFACE;
}

static ULONG STDMETHODCALLTYPE Calc_AddRef(void *This) {
    CalculatorImpl *pThis = (CalculatorImpl*)This;
    return (ULONG)InterlockedIncrement(&pThis->m_refCount);
}

static ULONG STDMETHODCALLTYPE Calc_Release(void *This) {
    CalculatorImpl *pThis = (CalculatorImpl*)This;
    ULONG count = (ULONG)InterlockedDecrement(&pThis->m_refCount);
    if (count == 0) {
        free(pThis);
    }
    return count;
}

static HRESULT STDMETHODCALLTYPE Calc_Add(void *This, double a, double b, double *result) {
    (void)This;
    if (!result) return E_POINTER;
    *result = a + b;
    return S_OK;
}

static HRESULT STDMETHODCALLTYPE Calc_Multiply(void *This, double a, double b, double *result) {
    (void)This;
    if (!result) return E_POINTER;
    *result = a * b;
    return S_OK;
}

static const ICalculatorVtbl g_CalculatorVtbl = {
    Calc_QueryInterface,
    Calc_AddRef,
    Calc_Release,
    Calc_Add,
    Calc_Multiply
};

CalculatorImpl* Calculator_Create(void) {
    CalculatorImpl *p = (CalculatorImpl*)malloc(sizeof(CalculatorImpl));
    if (!p) return NULL;
    p->lpVtbl = &g_CalculatorVtbl;
    p->m_refCount = 1;
    return p;
}
```
```cpp
class Calculator final : public ICalculator {
public:
    Calculator() : m_refCount(1) {}
    ~Calculator() = default;

    /* Реалізація методів IUnknown */
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void **ppvObject) override {
        if (!ppvObject) return E_POINTER;

        if (riid == __uuidof(IUnknown) || riid == IID_ICalculator) {
            *ppvObject = static_cast<ICalculator*>(this);
            AddRef();
            return S_OK;
        }

        *ppvObject = nullptr;
        return E_NOINTERFACE;
    }

    ULONG STDMETHODCALLTYPE AddRef() override {
        return ++m_refCount;
    }

    ULONG STDMETHODCALLTYPE Release() override {
        const ULONG count = --m_refCount;
        if (count == 0) {
            delete this;
        }
        return count;
    }

    /* Реалізація бізнес-методів ICalculator */
    HRESULT STDMETHODCALLTYPE Add(double a, double b, double *result) override {
        if (!result) return E_POINTER;
        *result = a + b;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE Multiply(double a, double b, double *result) override {
        if (!result) return E_POINTER;
        *result = a * b;
        return S_OK;
    }

private:
    std::atomic<ULONG> m_refCount;
};
```
:::

## 3. Фабрика класів та життєвий цикл сервера

Клієнт ніколи не створює COM-об'єкт безпосереднім викликом `malloc` або `new`, оскільки клієнтський виконуваний файл і DLL сервера можуть використовувати різні версії компілятора та різні менеджери динамічної пам'яті (CRT Heaps).

Створення екземпляра делегується фабриці класів — об'єкту, що реалізує інтерфейс `IClassFactory`. Фабрика надає метод `CreateInstance`, який виділяє пам'ять у локальній купі сервера та запитує початковий інтерфейс. Метод `LockServer` запобігає вивантаженню DLL операційною системою під час тривалих операцій.

:::tabs
```c
typedef struct ClassFactoryImpl {
    const IClassFactoryVtbl *lpVtbl;
    LONG m_refCount;
} ClassFactoryImpl;

static HRESULT STDMETHODCALLTYPE Factory_QueryInterface(void *This, REFIID riid, void **ppvObject) {
    if (!ppvObject) return E_POINTER;
    if (IsEqualGUID(riid, &IID_IUnknown) || IsEqualGUID(riid, &IID_IClassFactory)) {
        *ppvObject = This;
        ((ClassFactoryImpl*)This)->lpVtbl->AddRef(This);
        return S_OK;
    }
    *ppvObject = NULL;
    return E_NOINTERFACE;
}

static ULONG STDMETHODCALLTYPE Factory_AddRef(void *This) {
    return (ULONG)InterlockedIncrement(&((ClassFactoryImpl*)This)->m_refCount);
}

static ULONG STDMETHODCALLTYPE Factory_Release(void *This) {
    ULONG count = (ULONG)InterlockedDecrement(&((ClassFactoryImpl*)This)->m_refCount);
    if (count == 0) {
        free(This);
    }
    return count;
}

static HRESULT STDMETHODCALLTYPE Factory_CreateInstance(void *This, IUnknown *pUnkOuter, REFIID riid, void **ppvObject) {
    (void)This;
    if (pUnkOuter != NULL) return CLASS_E_NOAGGREGATION;
    if (!ppvObject) return E_POINTER;

    CalculatorImpl *calc = Calculator_Create();
    if (!calc) return E_OUTOFMEMORY;

    HRESULT hr = calc->lpVtbl->QueryInterface(calc, riid, ppvObject);
    calc->lpVtbl->Release(calc);
    return hr;
}

static HRESULT STDMETHODCALLTYPE Factory_LockServer(void *This, BOOL fLock) {
    (void)This; (void)fLock;
    return S_OK;
}

static const IClassFactoryVtbl g_FactoryVtbl = {
    Factory_QueryInterface,
    Factory_AddRef,
    Factory_Release,
    Factory_CreateInstance,
    Factory_LockServer
};

IClassFactory* ClassFactory_Create(void) {
    ClassFactoryImpl *f = (ClassFactoryImpl*)malloc(sizeof(ClassFactoryImpl));
    if (!f) return NULL;
    f->lpVtbl = &g_FactoryVtbl;
    f->m_refCount = 1;
    return (IClassFactory*)f;
}
```
```cpp
class CalculatorClassFactory final : public IClassFactory {
public:
    CalculatorClassFactory() : m_refCount(1) {}

    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void **ppvObject) override {
        if (!ppvObject) return E_POINTER;
        if (riid == __uuidof(IUnknown) || riid == __uuidof(IClassFactory)) {
            *ppvObject = static_cast<IClassFactory*>(this);
            AddRef();
            return S_OK;
        }
        *ppvObject = nullptr;
        return E_NOINTERFACE;
    }

    ULONG STDMETHODCALLTYPE AddRef() override {
        return ++m_refCount;
    }

    ULONG STDMETHODCALLTYPE Release() override {
        const ULONG count = --m_refCount;
        if (count == 0) {
            delete this;
        }
        return count;
    }

    HRESULT STDMETHODCALLTYPE CreateInstance(IUnknown *pUnkOuter, REFIID riid, void **ppvObject) override {
        if (pUnkOuter != nullptr) return CLASS_E_NOAGGREGATION;
        if (!ppvObject) return E_POINTER;

        auto *calc = new (std::nothrow) Calculator();
        if (!calc) return E_OUTOFMEMORY;

        const HRESULT hr = calc->QueryInterface(riid, ppvObject);
        calc->Release();
        return hr;
    }

    HRESULT STDMETHODCALLTYPE LockServer(BOOL fLock) override {
        (void)fLock;
        return S_OK;
    }

private:
    std::atomic<ULONG> m_refCount;
};
```
:::

У реальній бібліотеці DLL фабрика експортується системною точкою входу `DllGetClassObject`:

:::tabs
```c
STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, LPVOID *ppv) {
    if (!ppv) return E_POINTER;
    *ppv = NULL;

    if (IsEqualGUID(rclsid, &CLSID_Calculator)) {
        IClassFactory *factory = ClassFactory_Create();
        if (!factory) return E_OUTOFMEMORY;
        HRESULT hr = factory->lpVtbl->QueryInterface(factory, riid, ppv);
        factory->lpVtbl->Release(factory);
        return hr;
    }
    return CLASS_E_CLASSNOTAVAILABLE;
}
```
```cpp
STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, LPVOID *ppv) {
    if (!ppv) return E_POINTER;
    *ppv = nullptr;

    if (rclsid == CLSID_Calculator) {
        Microsoft::WRL::ComPtr<IClassFactory> factory;
        factory.Attach(new (std::nothrow) CalculatorClassFactory());
        if (!factory) return E_OUTOFMEMORY;

        return factory->QueryInterface(riid, ppv);
    }
    return CLASS_E_CLASSNOTAVAILABLE;
}
```
:::

## 4. Клієнтський код: безпечне керування ресурсами

Клієнтський потік перед початком будь-якої взаємодії з COM викликає `CoInitializeEx`, вказуючи бажану модель конкурентності (наприклад, `COINIT_APARTMENTTHREADED` для STA). Після завершення роботи обов'язково викликається `CoUninitialize`.

У коді мовою C клієнт змушений вручну контролювати кожен `Release()`. У коді C++ розумний покажчик `Microsoft::WRL::ComPtr` гарантує виклик `Release()` у деструкторі за принципом RAII, унеможливлюючи витоки пам'яті навіть за виникнення виключень.

:::tabs
```c
int main(void) {
    HRESULT hr = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED);
    if (FAILED(hr)) {
        printf("Помилка CoInitializeEx: 0x%08X\n", (unsigned int)hr);
        return 1;
    }

    /* Пряме отримання фабрики (імітація завантаження через SCM) */
    IClassFactory *pFactory = ClassFactory_Create();
    ICalculator *pCalc = NULL;

    hr = pFactory->lpVtbl->CreateInstance(pFactory, NULL, &IID_ICalculator, (void**)&pCalc);
    pFactory->lpVtbl->Release(pFactory);

    if (SUCCEEDED(hr) && pCalc) {
        double sum = 0.0;
        double prod = 0.0;

        pCalc->lpVtbl->Add(pCalc, 15.5, 24.5, &sum);
        pCalc->lpVtbl->Multiply(pCalc, 6.0, 7.0, &prod);

        printf("Результат додавання: %.2f\n", sum);
        printf("Результат множення: %.2f\n", prod);

        /* Ручне звільнення інтерфейсу */
        pCalc->lpVtbl->Release(pCalc);
    } else {
        printf("Не вдалося створити об'єкт калькулятора: 0x%08X\n", (unsigned int)hr);
    }

    CoUninitialize();
    return 0;
}
```
```cpp
int main() {
    const HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    if (FAILED(hr)) {
        std::cerr << "Помилка CoInitializeEx: 0x" << std::hex << hr << '\n';
        return 1;
    }

    {
        /* RAII-керування фабрикою та компонентом через ComPtr */
        Microsoft::WRL::ComPtr<IClassFactory> factory;
        factory.Attach(new CalculatorClassFactory());

        Microsoft::WRL::ComPtr<ICalculator> calc;
        const HRESULT createHr = factory->CreateInstance(
            nullptr,
            IID_ICalculator,
            reinterpret_cast<void**>(calc.GetAddressOf())
        );

        if (SUCCEEDED(createHr) && calc) {
            double sum = 0.0;
            double prod = 0.0;

            calc->Add(15.5, 24.5, &sum);
            calc->Multiply(6.0, 7.0, &prod);

            std::cout << "Результат додавання: " << sum << '\n';
            std::cout << "Результат множення: " << prod << '\n';
        } else {
            std::cerr << "Не вдалося отримати ICalculator: 0x" << std::hex << createHr << '\n';
        }
        /* Вказівники calc та factory автоматично викличуть Release() при виході з області видимості */
    }

    CoUninitialize();
    return 0;
}
```
:::

## 5. Типові інженерні пастки та правила передачі вказівників

1. **Правила володіння вказівниками (In, Out, In/Out):**
   - **`[in]`-параметри:** Клієнт передає вказівник у функцію і залишається його власником. Викликана функція лише читає об'єкт; якщо їй потрібно зберегти вказівник у власних структурах для асинхронного використання, вона зобов'язана викликати `AddRef()`.
   - **`[out]`-параметри:** Викликана функція створює об'єкт, викликає для нього `AddRef()` і записує адресу у вихідну змінну. Клієнт отримує повне право власності та зобов'язаний викликати `Release()`.
   - **`[in, out]`-параметри:** Клієнт передає живий об'єкт. Функція викликає `Release()` для старого об'єкта, записує новий і викликає `AddRef()` для нового.

2. **Запобігання циклічним посиланням (Cyclic References):**
   Якщо об'єкт `A` тримає інтерфейсний вказівник на об'єкт `B` (збільшивши його `refCount`), а `B` тримає вказівник на `A`, лічильники обох об'єктів ніколи не впадуть до нуля. Об'єкти назавжди зависнуть у пам'яті. У COM ця проблема вирішується слабкими посиланнями (Weak References), точками підключення подій (`IConnectionPoint`) або явними методами розриву зв'язку (`Close`/`Dispose`).

3. **Розподіл пам'яті на межі DLL (CoTaskMemAlloc):**
   Будь-які рядки або динамічні масиви, що передаються між модулями через `[out]`-параметри, повинні виділятися системним алокатором `CoTaskMemAlloc` і звільнятися клієнтом через `CoTaskMemFree`. Використання стандартного `malloc`/`free` неприпустиме, оскільки у різних компіляторах менеджери динамічної пам'яті ізольовані.
