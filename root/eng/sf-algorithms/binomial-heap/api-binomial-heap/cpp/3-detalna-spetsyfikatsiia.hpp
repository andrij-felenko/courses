// Еквівалентний C++ клас ds::BinomialHeap<T>
BinomialHeap();
~BinomialHeap();

NodeHandle insert(T key);
void merge(BinomialHeap& other);
std::optional<T> find_min() const;
T extract_min();
void decrease_key(NodeHandle handle, T new_key);
void delete_node(NodeHandle handle);
