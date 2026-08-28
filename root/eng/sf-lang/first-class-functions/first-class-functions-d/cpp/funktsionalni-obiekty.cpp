class __Lambda_Unique_Generated_Name {
private:
    int factor; // Захоплена змінна стає полем класу
public:
    __Lambda_Unique_Generated_Name(int f) : factor(f) {}

    int operator()(int x) const {
        return x * factor;
    }
};

// Створення об'єкта-функтора на стеку
__Lambda_Unique_Generated_Name multiply(factor);
