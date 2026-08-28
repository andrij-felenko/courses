class ProtectionHandler implements InvocationHandler {
    private final Object real;
    private final User user;
    // мапа: назва методу → потрібне право
    private static final Map<String, String> NEED = Map.of(
        "getOrder",    "orders:read",
        "placeOrder",  "orders:write",
        "cancelOrder", "orders:cancel");

    ProtectionHandler(Object real, User user) { this.real = real; this.user = user; }

    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        String need = NEED.get(method.getName());
        if (need != null && !user.can(need)) {          // одна точка охорони
            throw new AccessDeniedException(user.name() + ": немає права " + need);
        }
        return method.invoke(real, args);               // право є (або не потрібне) → делегуємо
    }
}
