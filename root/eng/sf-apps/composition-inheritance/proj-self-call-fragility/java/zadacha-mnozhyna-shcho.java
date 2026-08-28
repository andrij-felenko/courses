import java.util.*;

// Зламано — недоречне вживання спадкування!
class InstrumentedHashSet<E> extends HashSet<E> {
    private int addCount = 0;               // скільки елементів пробували додати

    @Override public boolean add(E e) {
        addCount++;                          // один елемент
        return super.add(e);
    }
    @Override public boolean addAll(Collection<? extends E> c) {
        addCount += c.size();                // ціла пачка
        return super.addAll(c);
    }

    public int getAddCount() { return addCount; }
}
