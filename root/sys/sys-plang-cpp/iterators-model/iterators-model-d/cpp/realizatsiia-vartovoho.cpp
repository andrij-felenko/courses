struct NullTerminatedSentinel {
    friend bool operator==(const char* it, NullTerminatedSentinel) {
        return *it == '\0'; // Умова зупинки — досягнення нульового байта
    }
};

const char* text = "Hello World";
// Замість strlen() передаємо асиметричну пару [const char*, NullTerminatedSentinel]
for (auto it = text; it != NullTerminatedSentinel{}; ++it) {
    std::cout << *it; // Однопрохідна обробка без попереднього сканування!
}
