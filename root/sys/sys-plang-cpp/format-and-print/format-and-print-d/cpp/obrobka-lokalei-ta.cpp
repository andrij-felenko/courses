#include <format>
#include <locale>
#include <iostream>

int main() {
    double num = 1234567.89;

    // Незалежно від локалі (завжди POSIX): "1234567.89"
    std::string default_fmt = std::format("{}", num);

    // З урахуванням потокової локалі L (наприклад, "1 234 567,89" або "1,234,567.89")
    std::string loc_fmt = std::format(std::locale("uk_UA.UTF-8"), "{:L}", num);
}
