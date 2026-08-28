// Історичний синтаксис C++0x ConceptGCC (2006-2009 роки):
concept LessThanComparable<typename T> {
    bool operator<(T a, T b);
    
    // Спроба формалізації математичних аксіом у мові:
    axiom Irreflexivity(T a) {
        (a < a) == false;
    }
    axiom Asymmetry(T a, T b) {
        if (a < b) (b < a) == false;
    }
};
