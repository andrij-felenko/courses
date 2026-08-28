// Було: контракт протікає — успадкували ВЕСЬ вектор
class Stack : public std::vector<int> {   // s.at(2), s.insert(...) — усе відкрито
public:
    void push(int x) { push_back(x); }
    int  pop() { int x = back(); pop_back(); return x; }
};

// Стало: вектор СХОВАНО полем, назовні лише push/pop
class Stack {
    std::vector<int> data;                // приватне — клієнт його не бачить
public:
    void push(int x) { data.push_back(x); }
    int  pop() { int x = data.back(); data.pop_back(); return x; }
    bool empty() const { return data.empty(); }
};
