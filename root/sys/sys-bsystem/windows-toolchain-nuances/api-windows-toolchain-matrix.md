# 📋 Довідкова матриця рантаймів, експорту та маніфестів Windows

Під час збірки складних C та C++ проєктів під Windows інженери постійно стикаються з розбіжностями між прапорцями компілятора MSVC, макросами препроцесора, бібліотеками імпорту та конфігураційними XML-маніфестами процесу. Ця довідкова матриця зводить докупи точні відповідності між ключами `cl.exe`, абстракціями CMake, компонуванням C Runtime (CRT), шаблонами експорту символів DLL та налаштуваннями середовища виконання Windows 10/11.

## Матриця рантаймів MSVC C/C++ (CRT)

У середовищі Microsoft Visual C++ стандартна бібліотека часу виконання (C Runtime, CRT) не є єдиним монолітним файлом. Залежно від того, як збирається проєкт — у режимі налагодження (Debug) чи випуску (Release), зі статичним включенням коду бібліотеки у виконуваний файл чи з динамічним завантаженням системних DLL, — компілятор обирає різні набори бібліотек, визначає специфічні макроси препроцесора та генерує відповідні директиви компонування.

Коли компілятор `cl.exe` обробляє вихідний файл, він автоматично записує у службову секцію об'єктного файлу `.drectve` спеціальні вказівки для лінкера у вигляді директив `/DEFAULTLIB:<назва_бібліотеки>`. Якщо скомпоновані об'єктні файли містять суперечливі директиви (наприклад, один вимагає `libcmt.lib`, а інший — `msvcrt.lib`), компонувальник `link.exe` зупиняє збірку з помилкою повторного визначення символів `LNK2005`.

| Прапорець `cl.exe` | Абстракція CMake (`MSVC_RUNTIME_LIBRARY`) | Визначені макроси | Статичні бібліотеки лінкування | Завантажувані DLL часу виконання |
| :--- | :--- | :--- | :--- | :--- |
| `/MD` | `MultiThreadedDLL` | `_MT`, `_DLL` | `msvcrt.lib`, `vcruntime.lib`, `ucrt.lib`, `msvcp.lib` | `vcruntime140.dll`, `msvcp140.dll`, `ucrtbase.dll` |
| `/MDd` | `MultiThreadedDebugDLL` | `_DEBUG`, `_MT`, `_DLL` | `msvcrtd.lib`, `vcruntimed.lib`, `ucrtd.lib`, `msvcpd.lib` | `vcruntime140d.dll`, `msvcp140d.dll`, `ucrtbased.dll` |
| `/MT` | `MultiThreaded` | `_MT` | `libcmt.lib`, `libvcruntime.lib`, `libucrt.lib`, `libcpmt.lib` | *Немає (усе вшито в бінарний образ)* |
| `/MTd` | `MultiThreadedDebug` | `_DEBUG`, `_MT` | `libcmtd.lib`, `libvcruntimed.lib`, `libucrtd.lib`, `libcpmtd.lib` | *Немає (усе вшито в бінарний образ)* |

### Керування рантаймом через абстракції CMake

У застарілих сценаріях збірки розробники часто намагалися змінити модель рантайму шляхом прямої заміни рядків у глобальних змінних `CMAKE_C_FLAGS` та `CMAKE_CXX_FLAGS` за допомогою регулярних виразів. Такий підхід є антипатерном, оскільки він ламає генератори мультиконфігураційних проєктів (Visual Studio, Ninja Multi-Config) та призводить до непередбачуваного змішування прапорців у зовнішніх підпроєктах.

Починаючи з CMake 3.15, вибір рантайму CRT здійснюється виключно через політику `CMP0091` та цільову властивість `MSVC_RUNTIME_LIBRARY`. Якщо для всього проєкту потрібен єдиний динамічний рантайм, розробник встановлює змінну `CMAKE_MSVC_RUNTIME_LIBRARY`, яка автоматично транслюється у коректні прапорці для кожної цільової конфігурації.

```cmake
# Встановлення для всього проєкту за замовчуванням (Release -> /MD, Debug -> /MDd)
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL")

# Або індивідуальне перевизначення для окремої службової утиліти (/MT або /MTd)
set_property(TARGET my_standalone_tool PROPERTY
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
)
```

## Шаблон заголовка міжплатформного експорту символів

Утиліти динамічного зв'язування на Windows та POSIX-системах працюють за діаметрально протилежними правилами. У Linux за замовчуванням усі символи глобальних функцій експортуються в динамічну таблицю `.dynsym`, якщо компілятору не передано прапорець `-fvisibility=hidden`. У Windows, навпаки, жоден символ не потрапляє до таблиці експорту DLL, доки розробник явно не позначить його атрибутом `__declspec(dllexport)` або не перелічить у файлі визначення модуля (`.def`).

При цьому для коду, який використовує функцію або клас з іншої DLL, оголошення має містити атрибут `__declspec(dllimport)`. Цей атрибут інформує компілятор про те, що адреса символу не є фіксованою константою часу лінкування, а витягується через вказівник у таблиці адрес імпорту (Import Address Table, IAT). Якщо бібліотека збирається як статичний архів (`.lib`), обидва атрибути (`dllexport` та `dllimport`) мають бути порожніми.

Наведений нижче шаблон реалізує безпечну схему макросів для чистих C та C++ бібліотек.

:::tabs
```c
/* mylib_export.h — версія для мови C */
#ifndef MYLIB_EXPORT_H
#define MYLIB_EXPORT_H

#if defined(MYLIB_STATIC_DEFINE)
    /* Для статичної бібліотеки атрибути експорту не потрібні */
    #define MYLIB_API
    #define MYLIB_LOCAL
#else
    #if defined(_WIN32) || defined(__CYGWIN__)
        #if defined(MYLIB_EXPORTS)
            /* Збірка DLL під Windows: експортуємо символи у EAT */
            #define MYLIB_API __declspec(dllexport)
        #else
            /* Споживання DLL під Windows: імпортуємо символи через IAT */
            #define MYLIB_API __declspec(dllimport)
        #endif
        #define MYLIB_LOCAL
    #else
        #if defined(__GNUC__) && __GNUC__ >= 4
            #define MYLIB_API   __attribute__((visibility("default")))
            #define MYLIB_LOCAL __attribute__((visibility("hidden")))
        #else
            #define MYLIB_API
            #define MYLIB_LOCAL
        #endif
    #endif
#endif

#endif /* MYLIB_EXPORT_H */
```
```cpp
// mylib_export.hpp — ідіоматична версія для C++
#ifndef MYLIB_EXPORT_HPP
#define MYLIB_EXPORT_HPP

#if defined(MYLIB_STATIC_DEFINE)
    // Статичне компонування: символи лінкуються безпосередньо
    #define MYLIB_API
    #define MYLIB_LOCAL
#else
    #if defined(_WIN32) || defined(__CYGWIN__)
        #if defined(MYLIB_EXPORTS)
            #define MYLIB_API __declspec(dllexport)
        #else
            #define MYLIB_API __declspec(dllimport)
        #endif
        #define MYLIB_LOCAL
    #else
        #if defined(__GNUC__) && __GNUC__ >= 4
            #define MYLIB_API   [[gnu::visibility("default")]]
            #define MYLIB_LOCAL [[gnu::visibility("hidden")]]
        #else
            #define MYLIB_API
            #define MYLIB_LOCAL
        #endif
    #endif
#endif

#endif // MYLIB_EXPORT_HPP
```
:::

## Автоматичний експорт символів та файли визначення модулів (`.def`)

Для проєктів, перенесених із середовища Linux, де розробники не розставляли атрибути `__declspec(dllexport)` у тисячах заголовків, CMake пропонує цільову властивість `WINDOWS_EXPORT_ALL_SYMBOLS`. Під час увімкнення цієї опції CMake запускає внутрішню утиліту `bindexplib.exe`, яка сканує всі згенеровані об'єктні файли (`.obj`), витягує з них глобальні імена символів (ігноруючи внутрішні службові символи компілятора на кшталт `DllMain` чи `type_info`) та автоматично створює тимчасовий текстовий файл визначення модуля з розширенням `.def`.

Компонувальник `link.exe` приймає цей файл через ключ `/DEF:exports.def` і експортує всі зазначені функції та змінні. Проте такий підхід має важливе технічне обмеження: формат двійкових образів PE/COFF використовує 16-бітне беззнакове ціле число для індексації таблиці порядкових номерів (Ordinal Table). Це обмежує максимальну кількість експортованих символів з однієї DLL числом 65 535. У разі перевищення лінкер видає фатальну помилку `LNK1189`.

```cmake
# Увімкнення автоматичної генерації .def файлу для цілі DLL
add_library(legacy_port SHARED
    src/algo.cpp
    src/parser.cpp
)
set_target_properties(legacy_port PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)
```

## Маніфест застосунку: UTF-8 та довгі шляхи (`app.manifest`)

Операційна система Windows історично підтримує двійкову модель прикладного маніфесту (Application Manifest). Маніфест — це XML-документ, що вбудовується безпосередньо в ресурси виконуваного PE-образу (тип ресурсу `RT_MANIFEST`, ідентифікатор `1` для `.exe` або `2` для `.dll`) або розміщується поруч у файловій системі як окремий файл з назвою `<програма>.exe.manifest`.

Починаючи з Windows 10 (оновлення 1903, збірка 18362), корпорація Microsoft додала можливість встановити кодування UTF-8 як активну кодову сторінку процесу через елемент `<activeCodePage>`. Це дозволяє стандартним ANSI-функціям Win32 API (`CreateFileA`, `fopen`, `getenv`, `SetCurrentDirectoryA`) приймати та повертати 8-бітні рядки у форматі UTF-8, усуваючи необхідність повної переписки кодової бази на виклики функцій з широкими символами `wchar_t` (`CreateFileW`).

Одночасно елемент `<longPathAware>` знімає історичне обмеження `MAX_PATH` у 260 символів для системних викликів, дозволяючи процесу звертатися до файлів із довжиною шляху до 32 767 символів без обов'язкового додавання низькорівневого префікса `\\?\`.

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
      version="1.0.0.0"
      processorArchitecture="*"
      name="CompanyName.ProductName.Application"
      type="win32"/>
  
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <!-- Увімкнення активної кодової сторінки UTF-8 для процесу (Windows 10 1903+) -->
      <activeCodePage xmlns="http://schemas.microsoft.com/SMI/2019/WindowsSettings">UTF-8</activeCodePage>
      <!-- Дозвіл на використання довгих шляхів понад 260 символів без префікса \\?\ -->
      <longPathAware xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">true</longPathAware>
    </windowsSettings>
  </application>
</assembly>
```

### Автоматичне вбудовування маніфесту через CMake

Для того, щоб CMake самостійно передав маніфест компонувальнику `link.exe` (який викличе інструмент маніфестів `mt.exe` або додасть прапорець `/MANIFESTINPUT`), достатньо вказати шлях до XML-файлу у списку вихідних файлів цілі:

```cmake
add_executable(my_application
    src/main.cpp
    "${CMAKE_CURRENT_SOURCE_DIR}/app.manifest"
)
```

## Ініціалізація консолі та кодових сторінок

Навіть якщо застосунок скомпільовано з прапорцем `/utf-8`, а рядкові літерали зберігаються в секції константних даних у форматі UTF-8, вивід у стандартний потік термінала Windows (`conhost.exe`) за замовчуванням призведе до появи спотворених символів (кракозябрів). Це пов'язано з тим, що буфер виводу консолі Windows історично налаштований на застарілу кодову сторінку виробника обладнання (OEM Code Page, наприклад, CP866 або CP437).

Щоб термінал інтерпретував байти як послідовності UTF-8, програма повинна викликати системні функції `SetConsoleOutputCP(CP_UTF8)` для виводу та `SetConsoleCP(CP_UTF8)` для вводу. У середовищі C++ для гарантованого повернення стану термінала до початкових значень при виході з програми використовують патерн RAII.

:::tabs
```c
/* console_utf8.c — налаштування консолі в C */
#include <windows.h>
#include <stdio.h>

int init_console_utf8(void) {
    /* Встановлюємо кодову сторінку виводу та вводу консолі в UTF-8 (CP 65001) */
    if (!SetConsoleOutputCP(CP_UTF8) || !SetConsoleCP(CP_UTF8)) {
        return 0;
    }
    return 1;
}

int main(void) {
    if (!init_console_utf8()) {
        fprintf(stderr, "Помилка конфігурації консолі UTF-8\n");
    }
    printf("Тестовий вивід Unicode: Привіт, світе! 🚀\n");
    return 0;
}
```
```cpp
// console_utf8.cpp — RAII-обгортка ініціалізації консолі в C++
#include <windows.h>
#include <iostream>

class ConsoleUtf8Guard {
public:
    ConsoleUtf8Guard() 
        : old_out_cp_(GetConsoleOutputCP()), 
          old_in_cp_(GetConsoleCP()) 
    {
        SetConsoleOutputCP(CP_UTF8);
        SetConsoleCP(CP_UTF8);
    }

    ~ConsoleUtf8Guard() noexcept {
        // Відновлюємо попередні кодові сторінки термінала
        SetConsoleOutputCP(old_out_cp_);
        SetConsoleCP(old_in_cp_);
    }

    ConsoleUtf8Guard(const ConsoleUtf8Guard&) = delete;
    ConsoleUtf8Guard& operator=(const ConsoleUtf8Guard&) = delete;

private:
    UINT old_out_cp_;
    UINT old_in_cp_;
};

int main() {
    const ConsoleUtf8Guard console_guard;
    std::cout << "Тестовий вивід Unicode: Привіт, світе! 🚀\n";
    return 0;
}
```
:::

## Зведення типових кодів помилок та діагностики

Невідповідність моделей компонування, рантаймів та файлових шляхів проявляється у вигляді специфічних системних винятків або діагностичних повідомлень компонувальника. Нижче наведено зведену таблицю причин виникнення цих проблем та точних інженерних дій для їхнього усунення.

| Код / Повідомлення | Походження | Причина виникнення | Спосіб усунення |
| :--- | :--- | :--- | :--- |
| `0xC0000374` (`STATUS_HEAP_CORRUPTION`) | Win32 NT Heap Manager | `free()` або `delete` викликано для адреси, виділеної іншим екземпляром CRT (`/MD` проти `/MT` або `/MDd`). | Забезпечити єдиний прапорець CRT для всіх модулів або звільняти пам'ять через експортовану функцію тієї самої DLL. |
| `LNK2005: symbol already defined` | `link.exe` | Змішування статичного (`libcmt.lib`) та динамічного (`msvcrt.lib`) рантаймів в одній команді компонування. | Узгодити `CMAKE_MSVC_RUNTIME_LIBRARY` у всіх підпроєктах або виключити зайві бібліотеки прапорцем `/NODEFAULTLIB`. |
| `LNK2019: unresolved external symbol` | `link.exe` | 1. Забуто атрибут `__declspec(dllimport)` або макрос `MYLIB_EXPORTS`.<br>2. Споживачу не передано згенерований файл `mylib.lib`. | Перевірити підключення `.lib` файлу до `target_link_libraries()` та правильність макросів експорту. |
| `LNK1189: library limit of 65535 objects exceeded` | `link.exe` | `CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS` експортував понад 65 535 символів (переповнення 16-бітної таблиці EAT). | Вимкнути авто-експорт та перейти на явні макроси `MYLIB_API` лише для публічного API бібліотеки. |
| `ERROR_PATH_NOT_FOUND` (код 3) | Win32 File API | Абсолютний шлях до файлу перевищив ліміт `MAX_PATH` (260 символів) без увімкнення `longPathAware` або префікса `\\?\`. | Увімкнути `<longPathAware>` у маніфесті або скоротити шлях кореневого каталогу збірки. |
