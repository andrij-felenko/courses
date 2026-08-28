void audit() const {
    assert(index_.size() == slots_.size());
    size_t n = 0;
    for (uint32_t i = head_; i != NIL; i = slots_[i].next) {
        auto it = index_.find(slots_[i].key);
        assert(it != index_.end() && it->second == i);   // індекс і список згодні
        ++n;
    }
    assert(n == slots_.size());                          // і в списку всі
}
