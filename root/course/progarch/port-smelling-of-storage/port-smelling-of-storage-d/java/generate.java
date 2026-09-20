// Об'єкт-значення ідентифікатора: перевірка інваріантів у момент створення
public record DeviceId(UUID value) {
    public DeviceId {
        if (value == null) {
            throw new IllegalArgumentException("Ідентифікатор пристрою не може бути порожнім.");
        }
    }

    public static DeviceId generate() {
        return new DeviceId(UUID.randomUUID());
    }

    public static DeviceId from(String raw) {
        if (raw == null || raw.isBlank()) {
            throw new IllegalArgumentException("Рядок ідентифікатора не може бути порожнім.");
        }
        try {
            return new DeviceId(UUID.fromString(raw.trim()));
        } catch (IllegalArgumentException ex) {
            throw new IllegalArgumentException("Некоректний формат ідентифікатора пристрою: " + raw, ex);
        }
    }
}
