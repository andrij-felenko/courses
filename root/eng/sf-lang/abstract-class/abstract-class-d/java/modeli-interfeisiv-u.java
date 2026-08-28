// Java: чіткий поділ на abstract class та interface
// Інтерфейс підтримує множинне наслідування поведінки (через default-методи),
// але категорично не має стану екземпляра (полів)
public interface SerializableProtocol {
    byte[] serialize();
    void deserialize(byte[] data);

    // Допоміжний метод за замовчуванням
    default int getVersion() { return 1; }
}
