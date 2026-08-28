import java.io.*;
import java.util.Map;

public final class Config implements Serializable {
    private static final Config INSTANCE = new Config();

    // ВАЖЛИВО: усі поля-посилання — transient (пояснення нижче)
    private transient Map<String, String> settings;

    private Config() { this.settings = loadFromDisk(); }

    public static Config getInstance() { return INSTANCE; }

    // движок серіалізації викличе це замість того, щоб віддати новий об'єкт
    private Object readResolve() throws ObjectStreamException {
        return INSTANCE;               // тимчасовий десеріалізований об'єкт викидається
    }
}
