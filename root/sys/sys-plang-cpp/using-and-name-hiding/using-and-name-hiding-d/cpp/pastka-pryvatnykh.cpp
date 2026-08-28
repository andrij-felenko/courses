class BaseService {
public:
    void execute(double value) {
        std::cout << "BaseService::execute(double)\n";
    }
};

class CustomService : public BaseService {
public:
    using BaseService::execute; // втягнули public execute(double)

private:
    void execute(int value) {   // закритий внутрішній помічник
        std::cout << "CustomService::execute(int) [private]\n";
    }
};

int main() {
    CustomService service;
    // service.execute(10); // ✗ ПОМИЛКА КОМПІЛЯЦІЇ!
}
