#include <string>
#include <vector>

// У C++ std::string відстежує розмір і місткість:
// конкатенація має амортизовану лінійну складність O(N)!
std::string buffer;
buffer.reserve(1024);
for (const auto& piece : pieces) {
    buffer += piece; // Швидке дописування в кінець без пошуку вартового
}
