// Java Reflection API: динамічна інтроспекція та виклик методів
import java.lang.reflect.Field;
import java.lang.reflect.Method;

public class ReflectionDemo {
    public static void inspectAndInvoke(Object obj) throws Exception {
        Class<?> clazz = obj.getClass();
        System.out.println("Клас: " + clazz.getName());

        // Читання всіх полів, включно з приватними
        for (Field field : clazz.getDeclaredFields()) {
            field.setAccessible(true); // Обхід контролю доступу
            System.out.println("  Поле: " + field.getName() + 
                               ", Тип: " + field.getType().getSimpleName() + 
                               ", Значення: " + field.get(obj));
        }

        // Динамічний пошук та виклик методу
        Method method = clazz.getDeclaredMethod("calculateTotal", double.class);
        method.setAccessible(true);
        Object result = method.invoke(obj, 15.5);
        System.out.println("Результат виклику: " + result);
    }
}
