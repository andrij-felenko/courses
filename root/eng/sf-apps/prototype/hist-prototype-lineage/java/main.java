public class Circle implements Cloneable {
    int x, y, r;

    @Override public Circle clone() {
        try {
            return (Circle) super.clone();   // магічне побайтове копіювання полів
        } catch (CloneNotSupportedException e) {
            throw new AssertionError(e);      // не станеться — ми ж Cloneable
        }
    }
}
