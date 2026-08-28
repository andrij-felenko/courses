// java.sql.Wrapper — стандартний «люк» крізь шари обгорток JDBC
interface Wrapper {
    <T> T unwrap(Class<T> iface) throws SQLException;   // дай справжній об'єкт під шарами
    boolean isWrapperFor(Class<?> iface);
}

// власний декоратор з'єднання вміє віддати вкладене:
class LoggingConnection implements Connection {   // Connection extends Wrapper
    private final Connection inner;
    LoggingConnection(Connection inner) { this.inner = inner; }
    // ...усі методи Connection делегуються на inner, з логуванням...

    @Override public <T> T unwrap(Class<T> iface) throws SQLException {
        if (iface.isInstance(inner)) return iface.cast(inner);  // це вже потрібний тип
        return inner.unwrap(iface);                             // ні — спускаємось глибше
    }
    @Override public boolean isWrapperFor(Class<?> iface) throws SQLException {
        return iface.isInstance(inner) || inner.isWrapperFor(iface);
    }
}
