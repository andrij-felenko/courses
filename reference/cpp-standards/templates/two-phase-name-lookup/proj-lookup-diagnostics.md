# ⚙️ Лабораторний стенд аналізу й усунення помилок двофазного пошуку

У цій практичній вставці детально розібрано п'ять комплексних інженерних сценаріїв збоїв компіляції та прихованих помилок виконання, спричинених специфікою двофазного пошуку імен у шаблонах C++. Для кожного сценарію наведено репродукцію проблеми, покроковий розбір аналізу компілятора на Фазі 1 та Фазі 2, а також ідіоматичні способи виправлення коду з порівняльним аналізом інженерних компромісів.

## Сценарій 1. Звернення до членів залежного базового класу

Найпоширенішою помилкою під час розробки шаблонних ієрархій є спроба викликати метод або звернутися до поля базового класу без явного вказівника `this->` або кваліфікатора області видимості, якщо базовий клас залежить від параметра шаблону `T`.

### Репродукція проблемного коду

Розглянемо практичний приклад процесора даних, у якому базовий клас керує конфігурацією та статусом, а похідний клас реалізує безпосередню обробку:

```cpp
#include <iostream>

template <typename T>
class BaseProcessor {
public:
    void initialize_hardware() {
        std::cout << "BaseProcessor: Hardware initialized\n";
    }

protected:
    int status_code = 200;
};

template <typename T>
class NetworkProcessor : public BaseProcessor<T> {
public:
    void process_packet(const T& packet) {
        // ПОМИЛКА КОМПІЛЯЦІЇ під час Фази 1 на GCC / Clang / MSVC /permissive-:
        // 'initialize_hardware' was not declared in this scope
        initialize_hardware();

        // ПОМИЛКА КОМПІЛЯЦІЇ під час Фази 1:
        // 'status_code' was not declared in this scope
        std::cout << "Packet status: " << status_code << "\n";
    }
};
```

### Покроковий розбір дій компілятора

1. **Аналіз синтаксису на Фазі 1:**
   Коли компілятор читає код класу `NetworkProcessor<T>`, він здійснює первинний аналіз синтаксичного дерева. Під час обробки функції `process_packet` компілятор зустрічає імена `initialize_hardware()` та `status_code`.
2. **Класифікація імен:**
   Оскільки у синтаксисі виклику `initialize_hardware()` немає жодного згадування параметра `T`, компілятор класифікує це ім'я як **незалежне ім'я (non-dependent name)**.
3. **Пошук у контексті визначення:**
   Для незалежного імені компілятор запускає негайний некваліфікований пошук у поточній області видимості `NetworkProcessor`, охопних просторах імен та глобальній області.
4. **Ігнорування залежної бази:**
   Базовий клас записано як `BaseProcessor<T>`. Оскільки `T` ще невідомий, `BaseProcessor<T>` є залежним базовим класом. Компілятор свідомо ігнорує вміст `BaseProcessor<T>` на Фазі 1, адже для деяких конкретних типів `T` клас `BaseProcessor` міг би бути частково спеціалізований і взагалі не мати вказаних членів.
5. **Результат трансляції:**
   Оскільки ім'я `initialize_hardware` не знайдено ні в `NetworkProcessor`, ні у глобальному просторі, компілятор спиняє збірку і видає помилку `use of undeclared identifier` вже на Фазі 1, навіть якщо клас `NetworkProcessor` жодного разу не створюється у програмі.

### Три інженерні рішення з порівняльним аналізом

Для виправлення коду необхідно зробити виклики залежними або явно ввести імена в область видимості похідного класу.

```cpp
template <typename T>
class FixedNetworkProcessor : public BaseProcessor<T> {
public:
    // ── Рішення 1: Явне використання this-> (Рекомендовано для методів) ──────
    void process_v1(const T& packet) {
        // Вказівник this має залежний тип FixedNetworkProcessor<T>*,
        // тому вираз this->initialize_hardware() стає залежним виразом.
        // Його пошук відкладається до Фази 2 і успішно знаходить метод у BaseProcessor<T>.
        this->initialize_hardware();
        std::cout << "Status: " << this->status_code << "\n";
    }

    // ── Рішення 2: Кваліфікація іменем базового класу ────────────────────────
    void process_v2(const T& packet) {
        // Запис BaseProcessor<T>:: містить параметр T, тому ім'я кваліфіковане і залежне.
        // УВАГА: Якщо initialize_hardware є VIRTUAL методом, такий запис ВИМИКАЄ
        // механізм віртуального виклику і здійснює прямий виклик функції базового класу!
        BaseProcessor<T>::initialize_hardware();
        std::cout << "Status: " << BaseProcessor<T>::status_code << "\n";
    }

    // ── Рішення 3: Введення імен через using (Рекомендовано для полів) ────────
    using BaseProcessor<T>::initialize_hardware;
    using BaseProcessor<T>::status_code;

    void process_v3(const T& packet) {
        // Завдяки using-оголошенню імена стають відомими у контексті класу на Фазі 1.
        // Виклики можна писати без префіксів у кожному методі класу.
        initialize_hardware();
        std::cout << "Status: " << status_code << "\n";
    }
};
```

> 🔧 **Інженерне правило:** Для викликів віртуальних методів базового шаблону завжди використовуйте `this->method()`. Для доступу до захищених полів або частих викликів простих методів використовуйте `using BaseProcessor<T>::member;` на початку класу.

---

## Сценарій 2. Порядок оголошення функцій і пастка невиділеного ADL

Другий поширений сценарій пов'язаний із ситуацією, коли шаблон посилається на вільну функцію, перевантажену для конкретного типу, але її оголошення розташоване нижче за текст шаблону.

### Репродукція проблемного коду

```cpp
#include <iostream>

// 1. Оголошення шаблону обробки
template <typename T>
void execute_workflow(T data) {
    // Виклик 1: 100 є значенням типу int — це НЕЗАЛЕЖНИЙ вирази!
    log_step_code(100);

    // Виклик 2: data має тип T — це ЗАЛЕЖНИЙ вираз!
    process_custom_data(data);
}

// 2. Функція для незалежного виклику оголошена ПІСЛЯ шаблону
void log_step_code(int code) {
    std::cout << "Step code: " << code << "\n";
}

namespace app {
    struct DataPayload {};

    // 3. Функція для залежного виклику у просторі користувача
    void process_custom_data(DataPayload) {
        std::cout << "App data payload processed\n";
    }
}

int main() {
    app::DataPayload payload;
    // execute_workflow(payload); // ПОМИЛКА під час компіляції!
}
```

### Покроковий розбір причин збою

1. **Аналіз `log_step_code(100)`:**
   Аргумент `100` має тип `int`. Це незалежний тип. Виклик `log_step_code(100)` є незалежним виразом. Компілятор шукає функцію `log_step_code(int)` на Фазі 1 у контексті визначення шаблону. Оскільки на момент читання тексту шаблону функція `log_step_code` ще не була оголошена, компілятор видає помилку `log_step_code was not declared in this scope`.
2. **Аналіз `process_custom_data(data)`:**
   Аргумент `data` має залежний тип `T`. Виклик `process_custom_data(data)` є залежним виразом. Пошук імені відкладається до Фази 2. Під час інстанціювання `execute_workflow<app::DataPayload>` у точці POI компілятор запускає ADL для типу `app::DataPayload`. Асоційованим простором є `app`. У просторі `app` компілятор успішно знаходить `process_custom_data(DataPayload)`.

### Рефакторинг та ідіоматичне виправлення

Щоб усунути помилку, усі незалежні функції повинні мати попереднє оголошення (forward declaration) до тексту шаблону.

```cpp
#include <iostream>

// КРОК 1: Попереднє оголошення незалежної функції для Фази 1
void log_step_code(int code);

// КРОК 2: Визначення шаблону
template <typename T>
void execute_workflow(T data) {
    log_step_code(100);        // Успішно зв'язується на Фазі 1
    process_custom_data(data); // Зв'язується на Фазі 2 через ADL
}

// Реалізація незалежної функції
void log_step_code(int code) {
    std::cout << "Step code: " << code << "\n";
}

namespace app {
    struct DataPayload {};
    void process_custom_data(DataPayload) {
        std::cout << "App data payload processed via ADL\n";
    }
}

int main() {
    app::DataPayload payload;
    execute_workflow(payload); // Збірка й виконання пройдуть ідеально!
}
```

---

## Сценарій 3. Приховані функції-друзі (Hidden Friends) та двофазний ADL

Третій складний сценарій виникає при спробі викликати приховану функцію-друга (англ. *hidden friend*), оголошену всередині іншого класу.

### Проблемний код

```cpp
#include <iostream>

namespace math {
    template <typename T>
    class Matrix {
        T value;
    public:
        Matrix(T v) : value(v) {}

        // Прихована функція-друг: оголошена ВСЕРЕДИНІ класу!
        // Вона НЕ бачиться через звичайний пошук у просторі math::
        friend Matrix operator+(const Matrix& a, const Matrix& b) {
            return Matrix(a.value + b.value);
        }

        friend void print_matrix(const Matrix& m) {
            std::cout << "Matrix value: " << m.value << "\n";
        }
    };
}

template <typename T>
void algorithm(T a, T b) {
    // Незалежний або залежний виклик?
    // math::Matrix<int> є залежним типом від T.
    auto res = a + b;       // Працює через ADL на Фазі 2
    print_matrix(res);     // Працює через ADL на Фазі 2
}

void global_helper() {
    // ПОМИЛКА: Звичайний некваліфікований пошук НЕ знаходить print_matrix!
    // print_matrix(math::Matrix<int>(5)); 
}
```

### Аналіз семантики Hidden Friend на двох фазах

Приховані функції-друзі — це функції, які визначені всередині класу з ключовим словом `friend`. Вони не додаються до зовнішнього простору імен для звичайного пошуку.

1. **На Фазі 1:** Для будь-якого незалежного виклику прихована функція-друг є повністю невидимою.
2. **На Фазі 2:** Коли виклик є залежним (`print_matrix(res)`), компілятор виконує ADL для типу `math::Matrix<int>`. Оскільки клас `Matrix<int>` є асоційованою сутністю для аргументу `res`, ADL заглядає всередину списку друзів класу `Matrix<int>` і знаходить `print_matrix`.

Цей прийом є стандартом для створення ефективних операторів та спеціалізованих функцій (наприклад `swap`), оскільки він захищає глобальний простір імен від засмічення та прискорює Фазу 1.

---

## Сценарій 4. Шаблони з довільною арністю (Variadic Templates) та вирази згортки

З появою C++11 та C++17 узагальнене програмування збагатилося шаблонами змінної арності (`Args...`) та виразами згортки (fold expressions). Вони створюють додаткові нюанси для двофазного пошуку.

### Проблемний код

```cpp
#include <iostream>

// Допоміжна функція для одинарного значення
template <typename T>
void print_element(const T& val) {
    std::cout << val << " ";
}

template <typename... Args>
void print_all(const Args&... args) {
    // У C++17 вираз згортки для некваліфікованого виклику print_element:
    (print_element(args), ...); 
}

namespace custom {
    struct MyData {
        int id;
    };

    // Перевантаження для MyData оголошене ПІСЛЯ шаблону print_all!
    void print_element(const MyData& d) {
        std::cout << "[MyData:" << d.id << "] ";
    }
}

int main() {
    custom::MyData d1{10}, d2{20};
    print_all(d1, d2); // Викличе custom::print_element через ADL на Фазі 2!
}
```

### Покрокова діагностика пакета аргументів

1. **Розпакування пакету у виразі згортки:**
   Вираз `(print_element(args), ...)` розгортається компілятором у послідовність викликів `print_element(arg1), print_element(arg2), ...`.
2. **Оцінка залежності в пакеті:**
   Оскільки кожен аргумент `arg_i` має параметр-пакет типів `Args...`, кожен із розгорнутих викликів є залежним виразом.
3. **Фаза 2 для кожного елемента:**
   У точці POI компілятор обчислює ADL незалежно для кожного елемента пакета. Для `custom::MyData` ADL заглядає у простір `custom` і успішно обирає `custom::print_element(const MyData&)`.

---

## Сценарій 5. Розбір розбіжностей MSVC `/permissive-` у legacy-проєктах

При переведенні масштабних C++ проєктів під Windows зі старих версій Visual Studio (2013/2015) на сучасний інструментарій Visual Studio 2022 із прапорцем `/permissive-` або стандартом `/std:c++20` виникає масивна хвиля помилок компіляції.

### Типовий фрагмент нестандартного legacy-коду MSVC

```cpp
// Заголовок LegacyBuffer.h
template <typename T>
class LegacyBuffer {
    T* storage;
    size_t length;

public:
    void reset() {
        // ПОМИЛКА 1 у C++20: ZeroMemory не знайдено на Фазі 1 (відсутній інклуд windows.h)
        ZeroMemory(storage, length * sizeof(T));

        // ПОМИЛКА 2 у C++20: typename обов'язковий перед залежним типом T::iterator
        T::iterator it = storage->begin();
    }
};

#include <windows.h> // Помилка архітектури: системний заголовок включено ПІСЛЯ шаблону!
```

### Алгоритм безпечної міграції legacy-коду

Для успішного переведення коду на суворий двофазний пошук слід виконати три кроки:

1. **Упорядкування заголовків (Header Hygiene):** Перенесіть включення всіх системних та бібліотечних заголовків (наприклад, `<windows.h>`, `<algorithm>`, `<vector>`) до оголошення шаблонів. Незалежні системні функції мусять бути відомими на Фазі 1.
2. **Розстановка дисамбігуаторів `typename`:** Додайте ключове слово `typename` перед усіма залежними кваліфікованими типами (`typename T::iterator`, `typename T::value_type`).
3. **Кваліфікація методів базових класів:** Додайте `this->` до всіх викликів методів базових залежних класів.

Дотримання цих трьох правил гарантує, що код буде однаково успішно компілюватися як на сучасних версіях MSVC з прапорцем `/permissive-`, так і на компіляторах GCC та Clang на будь-яких операційних системах.
