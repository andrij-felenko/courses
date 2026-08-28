std::unordered_map<std::string, int> word_counts;

// Розпакування пари ітератора та булевого прапорця
if (auto [it, inserted] = word_counts.try_emplace("packet", 1); inserted) {
    std::cout << "Вставлено нове слово з лічильником: " << it->second << "\n";
}

// Ітерація по асоціативному контейнеру
for (const auto& [word, count] : word_counts) {
    std::cout << word << ": " << count << "\n";
}
