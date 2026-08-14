# 📋 Довідник інтерфейсів та операцій std::filesystem

Цей технічний довідник містить повну специфікацію типів даних, сигнатур методів, переліків прапорців та вільних операційних функцій модуля файлової системи стандартної бібліотеки. Документ слугує точним орієнтиром для вибору підходящих методів обробки шляхів, налаштування прапорців обходу та обробки кодів системних помилок без зчитування документації конкретної реалізації компілятора.

## 1. Клас синтаксичного шляху та його внутрішній макет

Клас шляху представляє шлях у файловій системі в нативному форматі операційної системи. Об'єкт шляху інкапсулює нативний рядок символів та виконує суто синтаксичний аналіз тексту у оперативній пам'яті без звернення до дискового накопичувача.

```cpp
namespace std::filesystem {
    class path {
    public:
        using value_type = /* char для POSIX, wchar_t для Windows */;
        using string_type = std::basic_string<value_type>;
        static constexpr value_type preferred_separator = /* '/' для POSIX, '\\' для Windows */;

        // Конструктори та присвоєння
        path() noexcept;
        path(const path& p);
        path(path&& p) noexcept;
        template <class Source> path(const Source& source);
        template <class InputIt> path(InputIt first, InputIt last);

        // Присвоєння та модифікатори
        path& operator=(const path& p);
        path& operator=(path&& p) noexcept;
        path& assign(const string_type& source);
        path& operator/=(const path& p);
        path& append(const path& p);
        path& operator+=(const path& p);
        path& concat(const path& p);
        void clear() noexcept;
        path& make_preferred();
        path& remove_filename();
        path& replace_filename(const path& replacement);
        path& replace_extension(const path& replacement = path());
        void swap(path& rhs) noexcept;

        // Конверсії та представлення в пам'яті
        const string_type& native() const noexcept;
        const value_type* c_str() const noexcept;
        operator string_type() const;

        std::string string() const;
        std::wstring wstring() const;
        std::u8string u8string() const;
        std::u16string u16string() const;
        std::u32string u32string() const;

        // Компоненти синтаксичної декомпозиції
        path root_name() const;
        path root_directory() const;
        path root_path() const;
        path relative_path() const;
        path parent_path() const;
        path filename() const;
        path stem() const;
        path extension() const;

        // Синтаксичні перевірки
        bool empty() const noexcept;
        bool has_root_name() const;
        bool has_root_directory() const;
        bool has_root_path() const;
        bool has_relative_path() const;
        bool has_parent_path() const;
        bool has_filename() const;
        bool has_stem() const;
        bool has_extension() const;
        bool is_absolute() const;
        bool is_relative() const;

        // Нормалізація та ітератори
        path lexically_normal() const;
        path lexically_relative(const path& base) const;
        path lexically_proximate(const path& base) const;

        class iterator;
        using const_iterator = iterator;
        iterator begin() const;
        iterator end() const;
    };
}
```

### Призначення та семантика методів класу шляху

Конструктори класу шляху дозволяють конструювати об'єкт як зі звичайних рядків, так і з широких рядків чи послідовностей символів. Автоматичні оператори додування оперативно перевіряють наявність розділювача у лівому операнді й додають нативний розділювач лише у разі його відсутності.

Слід чітко розрізняти два оператори модифікації шляху:

- Оператор додування шляху зі слешем (апендинг): перевіряє, чи закінчується лівий операнд на розділювач. Якщо розділювача немає і лівий операнд не є порожнім, оператор вставляє нативний розділювач перед додуванням правого операнда.
- Оператор конкатенації рядків без слешу: просто додає символи правого операнда безпосередньо до кінця лівого рядка без вставки розділювача (наприклад, для додування розширення файлу).

Методи синтаксичної декомпозиції розбирають текстовий рядок шляху на складники без викликів до ядра операційної системи:

- Метод отримання кореневого імені повертає літеру диска в системі Windows (наприклад `C:`) або порожній шлях у POSIX-системах.
- Метод отримання кореневого каталогу повертає розділювач кореня каталогу (`/` або `\`).
- Метод отримання кореневого шляху комбінує кореневе ім'я та кореневий каталог.
- Метод отримання батьківського шляху повертає шлях до каталогу верхнього рівня без імені файлу.
- Метод отримання імені файлу повертає останній компонент шляху разом із його розширенням.
- Метод отримання базового імені повертає ім'я файлу без останнього розширення.
- Метод отримання розширення повертає текстову підстроку починаючи з останньої крапки у імені файлу.

### Синтаксичні властивості та лексична нормалізація

Лексична нормалізація виконує синтаксичну очистку шляху у оперативній пам'яті. Вона усуває дубльовані розділювачі каталогів, вилучає посилання на поточний каталог та згортає посилання на батьківський каталог там, де це можливо зробити синтаксично без звернення до диска.

Методи перевірки абсолютності перевіряють, чи містить шлях одночасно і кореневе ім'я, і кореневий каталог. Важливо пам'ятати, що синтаксична перевірка не перевіряє факт фізичного існування файлу на диску.

| Метод шляху | Вхідний шлях (POSIX) | Результат (POSIX) | Вхідний шлях (Windows) | Результат (Windows) |
| :--- | :--- | :--- | :--- | :--- |
| `root_name()` | `/usr/bin/app` | `""` | `C:\Windows\System32` | `"C:"` |
| `root_directory()` | `/usr/bin/app` | `"/"` | `C:\Windows\System32` | `"\"` |
| `root_path()` | `/usr/bin/app` | `"/"` | `C:\Windows\System32` | `"C:\"` |
| `relative_path()` | `/usr/bin/app` | `"usr/bin/app"` | `C:\Windows\System32` | `"Windows\System32"` |
| `parent_path()` | `/usr/bin/app` | `"/usr/bin"` | `C:\Windows\System32` | `"C:\Windows"` |
| `filename()` | `/usr/bin/app.tar.gz` | `"app.tar.gz"` | `C:\Data\log.txt` | `"log.txt"` |
| `stem()` | `/usr/bin/app.tar.gz` | `"app.tar"` | `C:\Data\log.txt` | `"log"` |
| `extension()` | `/usr/bin/app.tar.gz` | `".gz"` | `C:\Data\log.txt` | `".txt"` |

### Ітерація по компонентах шляху

Об'єкт шляху підтримує стандартні ітератори для послідовного обходу окремих синтаксичних елементів. Ітератор розбиває шлях на кореневе ім'я, кореневий каталог та окремі імена каталогів і файлу.

Під час ітерації по абсолютного шляху перший крок повертає кореневе ім'я (у Windows), другий крок повертає кореневий каталог, а наступні кроки повертають елементи каталогів без розділювачів.

## 2. Кешований елемент каталогу: std::filesystem::directory_entry

Клас кешованого елемента каталогу зберігає шлях до об'єкта та кешує його основні системні атрибути під час обходу каталогів. Це запобігає виконанню повторних системних викликів опитування стану для кожного файлу.

```cpp
namespace std::filesystem {
    class directory_entry {
    public:
        directory_entry() noexcept = default;
        explicit directory_entry(const std::filesystem::path& p);
        directory_entry(const std::filesystem::path& p, std::error_code& ec);

        void assign(const std::filesystem::path& p);
        void assign(const std::filesystem::path& p, std::error_code& ec);
        void replace_filename(const std::filesystem::path& p);
        void replace_filename(const std::filesystem::path& p, std::error_code& ec);
        void refresh();
        void refresh(std::error_code& ec) noexcept;

        const std::filesystem::path& path() const noexcept;
        operator const std::filesystem::path&() const noexcept;

        bool exists() const;
        bool exists(std::error_code& ec) const noexcept;
        bool is_block_file() const;
        bool is_character_file() const;
        bool is_directory() const;
        bool is_fifo() const;
        bool is_other() const;
        bool is_regular_file() const;
        bool is_socket() const;
        bool is_symlink() const;

        std::uintmax_t file_size() const;
        std::uintmax_t file_size(std::error_code& ec) const noexcept;
        std::uintmax_t hard_link_count() const;
        std::uintmax_t hard_link_count(std::error_code& ec) const noexcept;
        
        file_time_type last_write_time() const;
        file_time_type last_write_time(std::error_code& ec) const noexcept;

        file_status status() const;
        file_status status(std::error_code& ec) const noexcept;
        file_status symlink_status() const;
        file_status symlink_status(std::error_code& ec) const noexcept;

        bool operator==(const directory_entry& rhs) const noexcept;
        bool operator!=(const directory_entry& rhs) const noexcept;
        bool operator<(const directory_entry& rhs) const noexcept;
        bool operator<=(const directory_entry& rhs) const noexcept;
        bool operator>(const directory_entry& rhs) const noexcept;
        bool operator>=(const directory_entry& rhs) const noexcept;
    };
}
```

### Механізм кешування метаданих та оновлення

Під час обходу дерев каталогів ітератором елемент каталогу отримує атрибути безпосередньо з системного буфера обходу операційної системи. 

Методи перевірки типу файлу, зчитування розміру та часу модифікації використовують вже збережені кешовані значення. Якщо виникла потреба явного примусового оновлення кешованих даних із диска, використовується метод оновлення кешу.

Переваги використання методів елемента каталогу перед вільними функціями:

- Нульові накладні витрати: методи опитування типу та розміру беруть значення з оперативної пам'яті об'єкта без викликів ядра операційної системи.
- Захист від відмови доступу: усі методи перевірки атрибутів підтримують версії з кодом помилки.
- Зручність ітерації: об'єкт елемента каталогу легко перетворюється на посилання на шлях.

Різниця між методами опитування статусу та статусу символьного посилання:

- Метод опитування статусу автоматично слідує за символьним посиланням і повертає атрибути цільового об'єкта. Якщо символьне посилання є висячим, метод повертає статус відсутності файлу.
- Метод опитування статусу символьного посилання повертає атрибути самого файлу посилання без його розв'язання.

## 3. Ітератори обходу дерев каталогів

Стандартна бібліотека надає два класи ітераторів для послідовного обходу вмісту каталогів.

```cpp
namespace std::filesystem {
    enum class directory_options : std::uint16_t {
        none                     = 0,
        follow_directory_symlinks = 1,
        skip_permission_denied   = 2
    };

    constexpr directory_options operator|(directory_options lhs, directory_options rhs);
    constexpr directory_options operator&(directory_options lhs, directory_options rhs);
    constexpr directory_options operator^(directory_options lhs, directory_options rhs);
    constexpr directory_options operator~(directory_options val);
}
```

Налаштування обходу визначають поведінку ітераторів під час зустрічі з символьними посиланнями та захищеними каталогами:

- Варіант за замовчуванням: не слідує за символьними посиланнями на каталоги та генерує помилку при відмові доступу.
- Прапорець слідування символьним посиланням: дозволяє рекурсивно заходити у каталоги, на які вказують символьні посилання.
- Прапорець пропуску відмови доступу: примушує ітератор ігнорувати каталоги без прав читання замість переривання роботи.

### Ітератор однорівневого обходу

Клас однорівневого ітератора призначений для сканування лише початкового каталогу без занурення у підкаталоги.

```cpp
namespace std::filesystem {
    class directory_iterator {
    public:
        using iterator_category = std::input_iterator_tag;
        using value_type        = directory_entry;
        using difference_type   = std::ptrdiff_t;
        using pointer           = const directory_entry*;
        using reference         = const directory_entry&;

        directory_iterator() noexcept;
        explicit directory_iterator(const path& p);
        directory_iterator(const path& p, directory_options options);
        directory_iterator(const path& p, std::error_code& ec) noexcept;
        directory_iterator(const path& p, directory_options options, std::error_code& ec) noexcept;

        const directory_entry& operator*() const;
        const directory_entry* operator->() const;
        directory_iterator& operator++();
        directory_iterator& increment(std::error_code& ec) noexcept;

        bool operator==(const directory_iterator& rhs) const noexcept;
        bool operator!=(const directory_iterator& rhs) const noexcept;
    };
}
```

### Рекурсивний ітератор обходу вглиб

Клас рекурсивного ітератора виконує обхід усіх підкаталогів углиб за принципом обходу дерева.

```cpp
namespace std::filesystem {
    class recursive_directory_iterator {
    public:
        using iterator_category = std::input_iterator_tag;
        using value_type        = directory_entry;

        recursive_directory_iterator() noexcept;
        explicit recursive_directory_iterator(const path& p);
        recursive_directory_iterator(const path& p, directory_options options);
        recursive_directory_iterator(const path& p, std::error_code& ec) noexcept;
        recursive_directory_iterator(const path& p, directory_options options, std::error_code& ec) noexcept;

        directory_options options() const;
        int depth() const;
        bool recursion_pending() const;

        void pop();
        void pop(std::error_code& ec);
        void disable_recursion_pending();

        const directory_entry& operator*() const;
        const directory_entry* operator->() const;
        recursive_directory_iterator& operator++();
        recursive_directory_iterator& increment(std::error_code& ec) noexcept;
    };
}
```

Спеціалізовані методи рекурсивного ітератора надають повний контроль над обходом дерева:

- Метод отримання глибини повертає поточний рівень занурення у підкаталоги. Корневий каталог обходу відповідає глибині нуль.
- Метод заборони занурення відключає рекурсивний похід у поточний підкаталог для наступного кроку ітерації. Це корисно для ігнорування великих службових каталогів.
- Метод виходу на рівень вгору примусово завершує сканування поточного підкаталогу та повертає ітератор у батьківський каталог.

## 4. Класифікація типів файлів та битові маски прав доступу

Перелік типів файлів визначає категорії об'єктів файлової системи, які підтримуються стандартною бібліотекою.

```cpp
namespace std::filesystem {
    enum class file_type {
        none        = 0,
        not_found   = -1,
        regular     = 1,
        directory   = 2,
        symlink     = 3,
        block       = 4,
        character   = 5,
        fifo        = 6,
        socket      = 7,
        unknown     = 8
    };
}
```

Маска прав доступу базується на традиційній вісімковій системі прав доступу POSIX:

```cpp
namespace std::filesystem {
    enum class perms : std::uint32_t {
        none         = 0,
        
        owner_read   = 0400, owner_write  = 0200, owner_exec   = 0100, owner_all   = 0700,
        group_read   = 0040, group_write  = 0020, group_exec   = 0010, group_all   = 0070,
        others_read  = 0004, others_write = 0002, others_exec  = 0001, others_all  = 0007,
        
        all          = 0777,
        
        set_uid      = 04000,
        set_gid      = 02000,
        sticky_bit   = 01000,
        mask         = 07777,
        unknown      = 0xFFFF
    };
}
```

Класи стану файлу та інформації про дисковий простір об'єднують тип файлу, права доступу та загальні метрики дискового накопичувача:

```cpp
namespace std::filesystem {
    class file_status {
    public:
        explicit file_status(file_type ft = file_type::none, perms prms = perms::unknown) noexcept;
        file_type type() const noexcept;
        void type(file_type ft) noexcept;
        perms permissions() const noexcept;
        void permissions(perms prms) noexcept;
    };

    struct space_info {
        std::uintmax_t capacity;
        std::uintmax_t free;
        std::uintmax_t available;
    };
}
```

## 5. Вільні операційні функції файлової системи

Усі операційні функції розбиті на три основні категорії і надають двокамерний API обробки помилок.

### Операції опитування стану та метрик

```cpp
namespace std::filesystem {
    bool exists(file_status s) noexcept;
    bool exists(const path& p);
    bool exists(const path& p, std::error_code& ec) noexcept;

    bool is_regular_file(const path& p);
    bool is_regular_file(const path& p, std::error_code& ec) noexcept;

    bool is_directory(const path& p);
    bool is_directory(const path& p, std::error_code& ec) noexcept;

    bool is_symlink(const path& p);
    bool is_symlink(const path& p, std::error_code& ec) noexcept;

    bool is_empty(const path& p);
    bool is_empty(const path& p, std::error_code& ec);

    bool equivalent(const path& p1, const path& p2);
    bool equivalent(const path& p1, const path& p2, std::error_code& ec) noexcept;

    std::uintmax_t file_size(const path& p);
    std::uintmax_t file_size(const path& p, std::error_code& ec) noexcept;

    file_status status(const path& p);
    file_status status(const path& p, std::error_code& ec) noexcept;

    file_status symlink_status(const path& p);
    file_status symlink_status(const path& p, std::error_code& ec) noexcept;

    space_info space(const path& p);
    space_info space(const path& p, std::error_code& ec) noexcept;
}
```

### Операції модифікації та керування файлами

```cpp
namespace std::filesystem {
    bool create_directory(const path& p);
    bool create_directory(const path& p, std::error_code& ec) noexcept;

    bool create_directories(const path& p);
    bool create_directories(const path& p, std::error_code& ec);

    bool remove(const path& p);
    bool remove(const path& p, std::error_code& ec) noexcept;

    std::uintmax_t remove_all(const path& p);
    std::uintmax_t remove_all(const path& p, std::error_code& ec);

    void rename(const path& old_p, const path& new_p);
    void rename(const path& old_p, const path& new_p, std::error_code& ec) noexcept;

    void copy(const path& from, const path& to, copy_options options = copy_options::none);
    void copy(const path& from, const path& to, copy_options options, std::error_code& ec);

    bool copy_file(const path& from, const path& to, copy_options options = copy_options::none);
    bool copy_file(const path& from, const path& to, copy_options options, std::error_code& ec);
}
```

### Операції з посиланнями та канонічними шляхами

```cpp
namespace std::filesystem {
    path canonical(const path& p);
    path canonical(const path& p, std::error_code& ec);

    path weakly_canonical(const path& p);
    path weakly_canonical(const path& p, std::error_code& ec);

    path read_symlink(const path& p);
    path read_symlink(const path& p, std::error_code& ec);

    void create_symlink(const path& target, const path& link);
    void create_symlink(const path& target, const path& link, std::error_code& ec) noexcept;

    void create_hard_link(const path& target, const path& link);
    void create_hard_link(const path& target, const path& link, std::error_code& ec) noexcept;
}
```

## 6. Спеціалізований клас винятку файлової системи

При виклику версій функцій без коду помилки у разі виникнення системного збою генерується об'єкт винятку.

```cpp
namespace std::filesystem {
    class filesystem_error : public std::system_error {
    public:
        filesystem_error(const std::string& what_arg, std::error_code ec);
        filesystem_error(const std::string& what_arg, const path& p1, std::error_code ec);
        filesystem_error(const std::string& what_arg, const path& p1, const path& p2, std::error_code ec);

        const path& path1() const noexcept;
        const path& path2() const noexcept;
        const char* what() const noexcept override;
    };
}
```

Клас винятку зберігає не лише стандартний код помилки, але й два шляхи файлової системи, що приймали участь у операції. Це дозволяє сформувати вичерпне повідомлення про помилку у логах системних програм без додаткового опитування стану.
