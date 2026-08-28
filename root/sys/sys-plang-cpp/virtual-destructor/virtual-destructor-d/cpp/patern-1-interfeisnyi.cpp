class IService {
public:
    virtual ~IService() = default;

    // Заборона зрізання об'єктів
    IService(const IService&) = delete;
    IService& operator=(const IService&) = delete;
    IService(IService&&) = delete;
    IService& operator=(IService&&) = delete;

    virtual void execute() = 0;
};
