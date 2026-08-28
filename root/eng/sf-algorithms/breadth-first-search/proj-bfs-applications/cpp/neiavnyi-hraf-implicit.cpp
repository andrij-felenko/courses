#include <string>
#include <vector>
#include <unordered_set>
#include <queue>

int ladder_length_cpp(std::string begin_word, std::string end_word, const std::vector<std::string>& word_list) {
    std::unordered_set<std::string> dict(word_list.begin(), word_list.end());
    if (!dict.contains(end_word)) return 0;

    std::queue<std::pair<std::string, int>> q;
    q.push({begin_word, 1});

    while (!q.empty()) {
        auto [word, len] = q.front();
        q.pop();

        if (word == end_word) return len;

        for (std::size_t i = 0; i < word.length(); ++i) {
            char original = word[i];
            for (char c = 'a'; c <= 'z'; ++c) {
                word[i] = c;
                if (dict.contains(word)) {
                    dict.erase(word); // Вилучення замість visited!
                    q.push({word, len + 1});
                }
            }
            word[i] = original;
        }
    }
    return 0;
}
