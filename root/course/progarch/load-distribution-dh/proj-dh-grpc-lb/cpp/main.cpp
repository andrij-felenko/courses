// C++20: gRPC Server з розширеними параметрами ротації сокетів (Keepalive + GOAWAY)
#include <grpcpp/grpcpp.h>
#include <grpcpp/health_check_service_interface.h>
#include <chrono>
#include <memory>
#include <string_view>
#include <iostream>

using namespace std::chrono_literals;

class IngestServerFinalizer {
public:
    static std::unique_ptr<grpc::Server> CreateAndStart(std::string_view listen_addr) {
        grpc::ServerBuilder builder;
        builder.AddListeningPort(std::string(listen_addr), grpc::InsecureServerCredentials());

        // 1. MaxConnectionAge: Примусове надсилання GOAWAY через 1 годину (3600000 мс)
        builder.AddChannelArgument(GRPC_ARG_MAX_CONNECTION_AGE_MS, 3600000);
        
        // 2. MaxConnectionAgeGrace: Час (30 с) на завершення активних стримів після GOAWAY
        builder.AddChannelArgument(GRPC_ARG_MAX_CONNECTION_AGE_GRACE_MS, 30000);
        
        // 3. Keepalive настройки для виявлення "мертвих" Wi-Fi сокетів
        builder.AddChannelArgument(GRPC_ARG_KEEPALIVE_TIME_MS, 30000);
        builder.AddChannelArgument(GRPC_ARG_KEEPALIVE_TIMEOUT_MS, 10000);
        builder.AddChannelArgument(GRPC_ARG_KEEPALIVE_PERMIT_WITHOUT_CALLS, 1);

        std::unique_ptr<grpc::Server> server = builder.BuildAndStart();
        std::cout << "gRPC Ingest Server запущено на " << listen_addr << std::endl;
        return server;
    }
};
