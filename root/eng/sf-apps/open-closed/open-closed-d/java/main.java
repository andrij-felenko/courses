class CountingList<T> {
    protected int count = 0;
    void add(T x)              { count++; store(x); }
    void addAll(List<T> xs)    { for (T x : xs) add(x); }   // ← базова реалізація гукає власний add()
}

class LoggingList<T> extends CountingList<T> {
    @Override void add(T x)           { log(x);        super.add(x); }
    @Override void addAll(List<T> xs) { log("batch");  super.addAll(xs); }  // super.addAll → this.add → знову log(x)
}
