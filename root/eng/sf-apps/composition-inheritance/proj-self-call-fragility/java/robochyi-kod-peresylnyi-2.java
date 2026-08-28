// Обгортка з лічильником — композиція замість спадкування HashSet.
class InstrumentedSet<E> extends ForwardingSet<E> {
    private int addCount = 0;

    public InstrumentedSet(Set<E> s) { super(s); }   // загортаємо будь-яку Set

    @Override public boolean add(E e) {
        addCount++;
        return super.add(e);                          // → ForwardingSet.add → s.add
    }
    @Override public boolean addAll(Collection<? extends E> c) {
        addCount += c.size();
        return super.addAll(c);                       // → ForwardingSet.addAll → s.addAll
    }

    public int getAddCount() { return addCount; }
}
