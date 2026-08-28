// Успадкування: лічильник у нащадку HashSet
class InstrumentedHashSet<E> extends HashSet<E> {
    private int addCount = 0;

    @Override public boolean add(E e) {
        addCount++;                    // порахували один
        return super.add(e);
    }
    @Override public boolean addAll(Collection<? extends E> c) {
        addCount += c.size();          // порахували цілу пачку
        return super.addAll(c);
    }
    public int getAddCount() { return addCount; }
}
