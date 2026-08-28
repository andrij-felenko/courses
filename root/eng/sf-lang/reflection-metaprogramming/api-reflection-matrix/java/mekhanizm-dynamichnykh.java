UserProfileService proxy = (UserProfileService) Proxy.newProxyInstance(
    UserProfileService.class.getClassLoader(),
    new Class<?>[] { UserProfileService.class },
    new InvocationHandler() {
        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            System.out.println("Логування перед викликом: " + method.getName());
            Object result = method.invoke(targetInstance, args);
            System.out.println("Логування після виклику");
            return result;
        }
    }
);
