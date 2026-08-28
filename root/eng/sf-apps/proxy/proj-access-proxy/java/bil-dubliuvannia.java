// Java: java.lang.reflect.Proxy будує клас на льоту, усі виклики йдуть в invoke().
import java.lang.reflect.*;

class LoggingHandler implements InvocationHandler {
    private final Object real;
    LoggingHandler(Object real) { this.real = real; }

    // ← ЄДИНА точка: сюди приходить БУДЬ-ЯКИЙ виклик будь-якого методу інтерфейсу
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        log("→ " + method.getName() + Arrays.toString(args));
        Object result = method.invoke(real, args);   // делегуємо справжньому
        log("← " + method.getName() + " = " + result);
        return result;
    }
}

@SuppressWarnings("unchecked")
static <T> T loggingProxy(Class<T> iface, T real) {
    return (T) Proxy.newProxyInstance(
        iface.getClassLoader(),
        new Class<?>[]{ iface },          // ← лише ІНТЕРФЕЙСИ, не конкретні класи
        new LoggingHandler(real));
}

// Один проксі накриває весь інтерфейс:
OrderService service = loggingProxy(OrderService.class, new RealOrderService());
service.getOrder("ord-42");   // → invoke(method=getOrder) → лог + делегування
service.placeOrder(order);    // той самий invoke, окремого коду під метод немає
