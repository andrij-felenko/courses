#include <format>
#include <vector>
#include <map>
#include <string>

std::vector<int> nums = {10, 20, 30};
std::string v_out = std::format("{}", nums); // "[10, 20, 30]"

std::map<std::string, int> ages = {{"Alice", 25}, {"Bob", 30}};
std::string m_out = std::format("{}", ages); // "{\"Alice\": 25, \"Bob\": 30}"

// Специфікатор 'n' відключає зовнішні дужки контейнера
std::string raw_nums = std::format("{::#x}", nums); // "[0xa, 0x14, 0x1e]" (з внутрішнім специфікатором елемента)
