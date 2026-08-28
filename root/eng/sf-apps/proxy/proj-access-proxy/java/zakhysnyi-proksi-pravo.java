class AccessDeniedException extends RuntimeException {   // щоб клієнт міг упіймати
    AccessDeniedException(String msg) { super(msg); }
}

class ProtectedOrderService implements OrderService {
    private final OrderService real;    // кого захищаємо (делегат)
    private final User user;            // від чийого імені йдуть виклики
    ProtectedOrderService(OrderService real, User user) {
        this.real = real; this.user = user;
    }

    private void require(String permission) {
        if (!user.can(permission)) {    // одна точка перевірки для всіх методів
            throw new AccessDeniedException(user.name() + ": немає права " + permission);
        }
    }

    public Order getOrder(String id) {
        require("orders:read");         // спершу право...
        return real.getOrder(id);       // ...тоді делегуємо
    }
    public String placeOrder(Order order) {
        require("orders:write");
        return real.placeOrder(order);
    }
    public void cancelOrder(String id) {
        require("orders:cancel");
        real.cancelOrder(id);
    }
}
