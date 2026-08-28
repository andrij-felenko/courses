// Та сама база — але в C++ самовиклик оживає лише тому, що add/addAll оголошено virtual.
template <class E>
class Bag {
protected:
    std::vector<E> items;
public:
    virtual void add(const E& e)                 { items.push_back(e); }
    virtual void addAll(const std::vector<E>& c) { for (const E& e : c) add(e); }   // ← самовиклик
    virtual ~Bag() = default;
};

// Нащадок рахує — і ловить те саме подвоєння, що й з HashSet.
template <class E>
class CountingBag : public Bag<E> {
public:
    int count = 0;
    void add(const E& e)                 override { ++count;           Bag<E>::add(e); }
    void addAll(const std::vector<E>& c) override { count += c.size();  Bag<E>::addAll(c); }
};
// CountingBag<std::string> b; b.addAll({"a","b","c"});  →  b.count == 6, а не 3
