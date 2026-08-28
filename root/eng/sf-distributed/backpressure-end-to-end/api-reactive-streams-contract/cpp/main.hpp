#include <grpcpp/grpcpp.h>

namespace grpc {

template <class RequestType, class ResponseType>
class ServerReaderWriter {
public:
    // Вимикає автоматичне читання для переходу на кредитну модель
    // Запит на читання одного повідомлення з транспортного буфера ядра
    void Read(RequestType* msg, void* tag);

    // Запис повідомлення в буфер відправки
    void Write(const ResponseType& msg, void* tag);

    // Перевірка готовності мережевого буфера до прийому нових даних
    // true: буфер вільний (Low Watermark); false: буфер заповнений (High Watermark)
    // Доступно через Reactor API (grpc::ServerWriteReactor)
};

}
