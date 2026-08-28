// один InvocationHandler декорує ВСІ методи інтерфейсу заразом
Service proxy = (Service) Proxy.newProxyInstance(
    Service.class.getClassLoader(),
    new Class<?>[]{ Service.class },
    (obj, method, args) -> {
        long t0 = System.nanoTime();
        Object out = method.invoke(real, args);          // делегація до справжнього
        log(method.getName() + ": " + (System.nanoTime() - t0) + " ns");
        return out;                                       // те саме логування — для будь-якого методу
    });
