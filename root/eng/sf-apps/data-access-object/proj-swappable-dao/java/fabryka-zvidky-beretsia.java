public class DaoFactory {
    public enum Backend { SQL, MEMORY }

    private final Backend backend;
    private final DataSource ds;                          // потрібен лише для SQL
    private final InMemoryUserDao  memUsers  = new InMemoryUserDao();
    private final InMemoryOrderDao memOrders = new InMemoryOrderDao();

    private DaoFactory(Backend backend, DataSource ds) {
        this.backend = backend;
        this.ds = ds;
    }

    // джерело вирішує конфіг, а не місце виклику
    public static DaoFactory fromConfig(DataSource ds) {
        String name = System.getenv().getOrDefault("DAO_BACKEND", "SQL");
        return new DaoFactory(Backend.valueOf(name), ds);
    }

    public UserDao users() {
        return backend == Backend.SQL ? new SqlUserDao(ds) : memUsers;
    }
    public OrderDao orders() {
        return backend == Backend.SQL ? new SqlOrderDao(ds) : memOrders;
    }
}
