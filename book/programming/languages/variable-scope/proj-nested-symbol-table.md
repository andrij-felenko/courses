# ⚙️ Таблиця символів та ієрархія оточень: розв'язання імен на практиці

Кожен компілятор, інтерпретатор або аналізатор вихідного коду стикається із задачею зв'язування текстових ідентифікаторів у сирцевому файлі з конкретними комірками пам'яті, регістрами процесора або об'єктами значень. У мовах із лексичною областю видимості ця задача зводиться до побудови та підтримки ієрархічного ланцюжка **таблиць символів** (*symbol tables*) під час компіляції або **кадрів оточення** (*environment records*) під час інтерпретації.

Коли потік виконання заходить у новий блок коду (тіло функції, цикл `for`, блок `if` чи анонімний блок `{ ... }`), створюється новий кадр оточення. Цей кадр містить власну локальну таблицю зв'язувань імен і зберігає покажчик на свого статичного батька — лексичне оточення, всередині якого цей блок було описано в сирцевому тексті.

```
   ┌─────────────────────────────────────────────────────────┐
   │ Глобальне оточення (Global Environment)                │
   │ { "x": 10, "g_flag": 1 }            parent = NULL       │
   └───────────────────────────▲─────────────────────────────┘
                               │ (статичний покажчик parent)
   ┌───────────────────────────┴─────────────────────────────┐
   │ Оточення функції (Function Scope)                       │
   │ { "x": 20 }                         parent = Global     │
   └───────────────────────────▲─────────────────────────────┘
                               │ (статичний покажчик parent)
   ┌───────────────────────────┴─────────────────────────────┐
   │ Вкладений блок (Inner Block Scope)                      │
   │ { "y": 30 }                         parent = Function   │
   └─────────────────────────────────────────────────────────┘
```

---

### Механізм роботи лексичного дерева оточень

На відміну від простого плоского словника, лексичне дерево оточень має кілька критичних властивостей, які забезпечують роботу правил видимості:

1. **Оголошення змінної (`define`)**: Завжди виконується виключно в поточному (найглибшому) активному кадрі. Якщо в батьківському або глобальному оточенні вже існує змінна з таким самим ім'ям, нова локальна змінна затінює її (*shadowing*). Зовнішнє значення залишається недоторканим у своєму кадрі, але стає тимчасово недоступним для прямого звернення з поточного блоку.
2. **Лексичний пошук (`lookup`)**: Починається з поточного кадру. Якщо ідентифікатор знайдено локально — пошук негайно завершується. Якщо ні — алгоритм робить крок угору за покажчиком `parent` і перевіряє батьківський кадр. Процес повторюється рекурсивно до досягнення кореневого (глобального) оточення. Якщо ім'я не знайдено і в глобальному кадрі, генерується помилка компілятора `Undefined identifier` або виключення часу виконання.
3. **Модифікація значення (`assign`)**: На відміну від оголошення, операція присвоєння не створює новий запис у поточному блоці, якщо ім'я там відсутнє. Алгоритм підіймається вгору по дереву предків, знаходить найближчий кадр, де ця змінна була спочатку оголошена, і перезаписує її значення там. Це дозволяє вкладеним блокам і замиканням змінювати стан своїх зовнішніх контекстів.
4. **Керування пам'яттю та замикання**: Якщо на кадр оточення більше не посилається жоден блок і жодна функція, він має бути знищений. Проте якщо функція-замикання захоплює посилання на цей кадр і повертається у зовнішній світ, час життя кадру подовжується за допомогою лічильника посилань (*reference counting*) або збирача сміття.

---

### Практична реалізація: C та C++

Нижче наведено повноцінну реалізацію ієрархічного середовища. 

У вкладці **C** структуру реалізовано через явне виділення пам'яті в купі з лічильником посилань (`ref_count`) для підтримки замикань та ручним обходом ланцюжка предків.

У вкладці **C++** реалізація спирається на ідіоми сучасного стандарту: `std::shared_ptr` для автоматичного подовження життя захоплених оточень, `std::string_view` та `std::optional` для безпечного доступу до значень, а також спеціальний RAII-клас `ScopeGuard`, який автоматично керує входом у лексичний блок та виходом із нього навіть у разі виникнення виключень.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_BINDINGS 64

typedef struct {
    char name[32];
    int value;
} Binding;

typedef struct Environment {
    Binding bindings[MAX_BINDINGS];
    size_t count;
    struct Environment* parent;
    size_t ref_count; // Лічильник посилань для підтримки замикань
} Environment;

// Створення нового кадру оточення
Environment* env_create(Environment* parent) {
    Environment* env = (Environment*)malloc(sizeof(Environment));
    if (!env) return NULL;
    env->count = 0;
    env->parent = parent;
    env->ref_count = 1;
    if (parent) {
        parent->ref_count++;
    }
    return env;
}

// Звільнення пам'яті з урахуванням замикань та каскадного видалення предків
void env_release(Environment* env) {
    if (!env) return;
    env->ref_count--;
    if (env->ref_count == 0) {
        Environment* p = env->parent;
        free(env);
        if (p) {
            env_release(p);
        }
    }
}

// Оголошення змінної в поточному блоці (затінює однойменні зовнішні)
bool env_define(Environment* env, const char* name, int value) {
    for (size_t i = 0; i < env->count; ++i) {
        if (strcmp(env->bindings[i].name, name) == 0) {
            env->bindings[i].value = value;
            return true;
        }
    }
    if (env->count >= MAX_BINDINGS) return false;
    strncpy(env->bindings[env->count].name, name, 31);
    env->bindings[env->count].name[31] = '\0';
    env->bindings[env->count].value = value;
    env->count++;
    return true;
}

// Лексичний пошук ідентифікатора вгору по дереву
bool env_lookup(const Environment* env, const char* name, int* out_val) {
    const Environment* curr = env;
    while (curr != NULL) {
        for (size_t i = 0; i < curr->count; ++i) {
            if (strcmp(curr->bindings[i].name, name) == 0) {
                *out_val = curr->bindings[i].value;
                return true;
            }
        }
        curr = curr->parent; // крок до лексичного предка
    }
    return false;
}

// Зміна значення існуючої змінної у найближчому видимому кадрі
bool env_assign(Environment* env, const char* name, int value) {
    Environment* curr = env;
    while (curr != NULL) {
        for (size_t i = 0; i < curr->count; ++i) {
            if (strcmp(curr->bindings[i].name, name) == 0) {
                curr->bindings[i].value = value;
                return true;
            }
        }
        curr = curr->parent;
    }
    return false;
}

int main(void) {
    // 1. Створення глобального оточення
    Environment* global_env = env_create(NULL);
    env_define(global_env, "x", 10);
    env_define(global_env, "g_flag", 1);

    // 2. Вхід у блок функції: створюємо дочірній кадр
    Environment* func_env = env_create(global_env);
    env_define(func_env, "x", 20); // Затінення global 'x'

    // 3. Вхід у вкладений блок (наприклад, тіло if)
    Environment* block_env = env_create(func_env);
    env_define(block_env, "y", 30);

    int val = 0;
    // Блок бачить локальний затінений x = 20
    env_lookup(block_env, "x", &val);
    printf("Block sees x = %d (expected 20)\n", val);

    // Блок бачить глобальний g_flag = 1 через ланцюжок предків
    env_lookup(block_env, "g_flag", &val);
    printf("Block sees g_flag = %d (expected 1)\n", val);

    // Мутація глобальної змінної з вкладеного блоку
    env_assign(block_env, "g_flag", 99);
    env_lookup(global_env, "g_flag", &val);
    printf("Global g_flag after assign = %d (expected 99)\n", val);

    // Вихід із блоків та коректне звільнення пам'яті
    env_release(block_env);
    env_release(func_env);
    env_release(global_env);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <optional>

class Environment : public std::enable_shared_from_this<Environment> {
public:
    using Ptr = std::shared_ptr<Environment>;

    explicit Environment(Ptr parent = nullptr) : parent_(std::move(parent)) {}

    // Оголошення в поточному кадрі (затінення зовнішніх імен)
    void define(std::string_view name, int value) {
        bindings_[std::string(name)] = value;
    }

    // Лексичний пошук ідентифікатора вгору по дереву
    [[nodiscard]] std::optional<int> lookup(std::string_view name) const noexcept {
        const auto it = bindings_.find(std::string(name));
        if (it != bindings_.end()) {
            return it->second;
        }
        if (parent_) {
            return parent_->lookup(name); // Рекурсивний підйом до предка
        }
        return std::nullopt;
    }

    // Зміна значення у найближчому видимому кадрі
    bool assign(std::string_view name, int value) noexcept {
        const auto it = bindings_.find(std::string(name));
        if (it != bindings_.end()) {
            it->second = value;
            return true;
        }
        if (parent_) {
            return parent_->assign(name, value);
        }
        return false;
    }

    [[nodiscard]] Ptr parent() const noexcept { return parent_; }

private:
    std::unordered_map<std::string, int> bindings_;
    Ptr parent_;
};

// RAII Scope Guard для автоматичного керування межами блоків
class ScopeGuard {
public:
    explicit ScopeGuard(Environment::Ptr& current)
        : current_ref_(current), previous_(current) {
        current_ref_ = std::make_shared<Environment>(previous_);
    }

    ~ScopeGuard() noexcept {
        current_ref_ = previous_; // Відновлюємо попередній кадр при виході з блоку
    }

    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;

private:
    Environment::Ptr& current_ref_;
    Environment::Ptr previous_;
};

int main() {
    auto current_env = std::make_shared<Environment>();
    current_env->define("x", 10);
    current_env->define("g_flag", 1);

    {
        // Вхід у блок функції через RAII
        ScopeGuard func_scope(current_env);
        current_env->define("x", 20); // Затінення

        {
            // Вхід у вкладений блок if/for
            ScopeGuard block_scope(current_env);
            current_env->define("y", 30);

            std::cout << "Block sees x = " << *current_env->lookup("x") << " (expected 20)\n";
            std::cout << "Block sees g_flag = " << *current_env->lookup("g_flag") << " (expected 1)\n";

            current_env->assign("g_flag", 99);
        } // block_scope автоматично знищується тут

        std::cout << "Func sees x = " << *current_env->lookup("x") << " (expected 20)\n";
        std::cout << "Func sees y = " 
                  << (current_env->lookup("y").has_value() ? "found" : "nullopt") << "\n";
    } // func_scope автоматично знищується тут

    std::cout << "Global sees x = " << *current_env->lookup("x") << " (expected 10)\n";
    std::cout << "Global g_flag = " << *current_env->lookup("g_flag") << " (expected 99)\n";

    return 0;
}
```
:::

---

### Покрокове трасування розв'язання імен

Щоб чітко уявити, що відбувається у структурах даних під час виконання коду, простежимо покрокову еволюцію таблиці символів:

1. **Крок 1 (Старт `global_env`)**:
   - `global_env` містить пари: `{"x": 10, "g_flag": 1}`.
   - `parent` = `NULL`, `ref_count` = 1.
2. **Крок 2 (Створення `func_env`)**:
   - Створюється `func_env` із `parent = global_env`.
   - `global_env->ref_count` збільшується до 2.
   - Оголошення `x = 20` записується у `func_env`. Тепер `lookup("x")` з цього кадру миттєво повертає 20, не звертаючись до глобального батька.
3. **Крок 3 (Створення `block_env`)**:
   - `block_env` створюється з `parent = func_env`.
   - Запис `y = 30` потрапляє у `block_env`.
   - Виклик `assign("g_flag", 99)` перевіряє `block_env` (немає), підіймається у `func_env` (немає), підіймається у `global_env` (знайдено!) і змінює комірку у глобальному кадрі.
4. **Крок 4 (Вихід із блоків `ScopeGuard`)**:
   - Знищення `block_scope` повертає покажчик `current_env` назад на `func_env`. Пам'ять `block_env` вивільняється.
   - Знищення `func_scope` повертає покажчик на `global_env`. Кадр `func_env` знищується, а `global_env->ref_count` повертається до 1.

---

### Архітектурні виклики та оптимізації в реальних компіляторах

У навчальних інтерпретаторах наведена схема з покажчиками `parent` та хеш-таблицями працює бездоганно. Проте у високонавантажених промислових віртуальних машинах (наприклад, V8 у Google Chrome або CPython) прямий пошук за рядковими ключами у ланцюжку кадрів створює неприйнятні накладні витрати:

1. **Швидкість пошуку `O(N)` проти векторів відображення (Display Vectors)**:
   Якщо функція викликається всередині п'яти рівнів вкладених блоків, звернення до глобальної змінної вимагає п'яти послідовних розіменувань покажчиків та п'яти запитів до хеш-таблиць.
   Щоб прискорити доступ, компілятори на етапі статичного аналізу транслюють кожне ім'я змінної у пару чисел: **`(глибина_лексичного_рівня, номер_слота_у_фреймі)`**. 
   Це так звані *індекси де Брейна* (*De Bruijn indices*). Під час виконання віртуальна машина звертається до масиву кадрів за прямим числовим індексом за `O(1)` без використання рядкових імен.
2. **Циклічні посилання замикань**:
   Якщо замикання зберігає посилання на свій кадр оточення, а в цьому самому кадрі зберігається посилання на саме замикання (класичний випадок рекурсивної лямбда-функції), виникає кільцеве посилання. 
   У мовах із простим підрахунком посилань (`std::shared_ptr` у C++ або старі версії PHP) ці об'єкти ніколи не будуть вивільнені з пам'яті самостійно. Для розриву таких циклів середовища виконання застосовують трасувальні збирачі сміття (*tracing garbage collectors*) або вимагають використання слабких покажчиків (`std::weak_ptr`).
3. **Ескейп-аналіз (Escape Analysis)**:
   Створення об'єкта оточення в купі для кожної функції є ресурсомістким через фрагментацію та роботу алокатора. Компілятори (такі як Go або HotSpot JVM) виконують статичний аналіз коду: якщо замикання не передається назовні функції та не зберігається в глобальних структурах, його змінні виділяються безпосередньо на швидкому апаратному стеку.
4. **Обробка взаємної рекурсії (`letrec`)**:
   Якщо дві функції викликають одна одну і обидві захоплюють лексичне оточення, виникає проблема порядку ініціалізації: функція `A` потребує імені `B` до того, як `B` буде сконструйовано. Для розв'язання цієї проблеми компілятори спочатку резервують порожні слоти для обох функцій у поточному кадрі оточення, і лише після цього обчислюють тіла замикань, заповнюючи слоти готовими покажчиками.
