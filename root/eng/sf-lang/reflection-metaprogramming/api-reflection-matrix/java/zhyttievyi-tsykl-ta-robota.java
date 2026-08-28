// Отримання та маніпуляція полями
Class<?> clazz = UserProfile.class;
Field field = clazz.getDeclaredField("secretToken");

// Примусове вимкнення перевірок контролю доступу JVM
field.setAccessible(true);

// Читання та модифікація стану об'єкта
Object value = field.get(userInstance);
field.set(userInstance, "new_secret_value");

// Динамічний пошук та виклик методу
Method method = clazz.getDeclaredMethod("updateBalance", double.class, boolean.class);
method.setAccessible(true);
Object result = method.invoke(userInstance, 100.50, true);
