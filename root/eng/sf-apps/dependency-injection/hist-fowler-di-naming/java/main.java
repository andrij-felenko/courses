// «Чиста» четверта форма: на КОЖНУ залежність — свій інтерфейс упорскування
public interface InjectPaymentGateway {
    void injectGateway(PaymentGateway gateway);
}

public class OrderService implements InjectPaymentGateway {
    private PaymentGateway gateway;

    public void injectGateway(PaymentGateway gateway) {
        this.gateway = gateway;   // контейнер гукне це сам
    }
}
