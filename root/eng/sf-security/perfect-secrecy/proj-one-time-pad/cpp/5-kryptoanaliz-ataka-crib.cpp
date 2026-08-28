#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <cctype>
#include <numeric>
#include <iomanip>

class CribDragger {
public:
    static std::vector<uint8_t> xorBuffers(std::span<const uint8_t> a, std::span<const uint8_t> b) {
        size_t n = std::min(a.size(), b.size());
        std::vector<uint8_t> res(n);
        for (size_t i = 0; i < n; ++i) {
            res[i] = a[i] ^ b[i];
        }
        return res;
    }

    static double calculateIC(std::span<const uint8_t> data) {
        if (data.size() < 2) return 0.0;
        size_t freq[256] = {0};
        for (uint8_t b : data) freq[b]++;

        double sum = 0.0;
        for (size_t count : freq) {
            sum += static_cast<double>(count * (count - 1));
        }
        double n = static_cast<double>(data.size());
        return sum / (n * (n - 1.0));
    }

    static bool isReadableAscii(std::span<const uint8_t> data) {
        for (uint8_t b : data) {
            if (b < 32 || b > 126) {
                if (b != 9 && b != 10 && b != 13) return false;
            }
        }
        return true;
    }

    static void drag(std::span<const uint8_t> diff, std::string_view crib) {
        std::cout << "\n--- Пошук слова-здогадки (Crib): \"" << crib << "\" ---\n";
        if (crib.size() > diff.size()) return;

        for (size_t offset = 0; offset <= diff.size() - crib.size(); ++offset) {
            std::vector<uint8_t> candidate(crib.size());
            for (size_t j = 0; j < crib.size(); ++j) {
                candidate[j] = diff[offset + j] ^ static_cast<uint8_t>(crib[j]);
            }

            if (isReadableAscii(candidate)) {
                std::string candStr(candidate.begin(), candidate.end());
                std::cout << "  Зсув " << offset << ": m2 = \"" << candStr << "\"\n";
            }
        }
    }
};

int main() {
    std::string_view p1 = "CONFIDENTIAL: THE PRESIDENT WILL ARRIVE AT 0800 HOURS AT NORTH GATE.";
    std::string_view p2 = "TOP_SECRET_MSG: WE HAVE EVACUATED ALL PERSONNEL ACROSS THE RIVER NOW.";

    // Спільний ключ для обох повідомлень
    std::vector<uint8_t> key(p1.size(), 0x7F); // Демонстраційний фіксований ключ
    std::vector<uint8_t> c1(p1.size()), c2(p2.size());
    for (size_t i = 0; i < p1.size(); ++i) c1[i] = static_cast<uint8_t>(p1[i]) ^ key[i];
    for (size_t i = 0; i < p2.size(); ++i) c2[i] = static_cast<uint8_t>(p2[i]) ^ key[i];

    // Криптоаналітик отримує різницю двох шифротекстів
    std::vector<uint8_t> diff = CribDragger::xorBuffers(c1, c2);

    std::cout << "Індекс збігів XOR (IC): " << std::fixed << std::setprecision(5) 
              << CribDragger::calculateIC(diff) << "\n";

    CribDragger::drag(diff, " PRESIDENT ");
    CribDragger::drag(diff, " PERSONNEL ");
    CribDragger::drag(diff, " EVACUATED ");

    return 0;
}
