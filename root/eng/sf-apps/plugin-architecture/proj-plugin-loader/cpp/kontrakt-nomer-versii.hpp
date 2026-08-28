// contract.h — це знають ОБИДВІ сторони: і ядро, і кожен автор плагіна.
#pragma once
#include <cstdint>
#include <string>
#include <vector>

// Номер версії контракту. Піднімаємо його ЩОРАЗУ, коли міняємо форму гнізда
// так, що старі плагіни перестають працювати (несумісна зміна).
inline constexpr int HOST_API = 3;

struct Block { std::string title; std::string body; };
struct Document { std::vector<Block> blocks; };

struct Exporter {
    virtual std::string extension() const = 0;                              // "pdf", "html", "md"
    virtual std::vector<std::uint8_t> exportDoc(const Document&) const = 0; // документ -> байти
    virtual ~Exporter() = default;
};

struct Host {
    // Вузьке вікно, яке ядро дає плагінові. НІЧОГО, крім цього, плагін
    // про ядро не знає — і не може дотягтись до його нутрощів.
    virtual void registerExporter(Exporter* e) = 0;
    virtual ~Host() = default;
};

// Умовлена форма плагіна: спільна бібліотека ЗОБОВ'ЯЗАНА виставити НАЗОВНІ
// два символи з C-зв'язуванням (стабільні, без манглінгу імена в .so).
// export/register — ключові слова C++, тож точка входу зветься plugin_register:
//   extern "C" const int PLUGIN_API = 3;
//   extern "C" void plugin_register(Host& host);
