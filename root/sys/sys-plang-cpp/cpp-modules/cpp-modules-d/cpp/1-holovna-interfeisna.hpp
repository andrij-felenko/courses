// Файл: network.cppm
export module network;

export namespace net {

class TcpSocket {
public:
    TcpSocket();
    ~TcpSocket();
    void connect(const char* host, int port);
    void send(const char* data, int len);
private:
    int m_native_handle{-1};
};

} // namespace net
