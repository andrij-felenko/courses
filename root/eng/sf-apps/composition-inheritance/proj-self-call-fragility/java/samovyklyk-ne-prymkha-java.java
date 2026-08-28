// База, чий пачковий метод САМ кличе перевизначуваний add — самовиклик як на долоні.
class Bag<E> {
    protected List<E> items = new ArrayList<>();
    public void add(E e)                { items.add(e); }
    public void addAll(Collection<E> c) { for (E e : c) add(e); }   // ← самовиклик
}

// Нащадок рахує — і ловить те саме подвоєння, що й з HashSet.
class CountingBag<E> extends Bag<E> {
    int count = 0;
    @Override public void add(E e)                { count++;          super.add(e); }
    @Override public void addAll(Collection<E> c) { count += c.size(); super.addAll(c); }
}
// new CountingBag<String>().addAll(List.of("a","b","c"))  →  count = 6, а не 3
