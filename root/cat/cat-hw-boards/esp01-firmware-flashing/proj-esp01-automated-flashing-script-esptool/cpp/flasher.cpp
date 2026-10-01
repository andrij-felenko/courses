#include "flasher.hpp"
#include <iostream>
#include <thread>
#include <algorithm>
#include <cstring>

EspFlasher::EspFlasher(const std::string& port_name, uint32_t baud_rate)
    : port_name_(port_name), baud_rate_(baud_rate) {}

EspFlasher::~EspFlasher() {
    close_port();
}

bool EspFlasher::open_port() {
#if defined(_WIN32)
    std::string full_name = "\\\\.\\" + port_name_;
    handle_ = CreateFileA(full_name.c_str(), GENERIC_READ | GENERIC_WRITE, 0, NULL, OPEN_EXISTING, 0, NULL);
    if (handle_ == INVALID_HANDLE_VALUE) {
        return false;
    }

    DCB dcb = {0};
    dcb.DCBlength = sizeof(DCB);
    GetCommState(handle_, &dcb);
    dcb.BaudRate = baud_rate_;
    dcb.ByteSize = 8;
    dcb.Parity = NOPARITY;
    dcb.StopBits = ONESTOPBIT;
    dcb.fDtrControl = DTR_CONTROL_DISABLE;
    dcb.fRtsControl = RTS_CONTROL_DISABLE;
    SetCommState(handle_, &dcb);

    COMMTIMEOUTS timeouts = {0};
    timeouts.ReadIntervalTimeout = 50;
    timeouts.ReadTotalTimeoutConstant = 200;
    timeouts.ReadTotalTimeoutMultiplier = 10;
    SetCommTimeouts(handle_, &timeouts);
    return true;
#else
    fd_ = open(port_name_.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd_ < 0) {
        return false;
    }
    fcntl(fd_, F_SETFL, 0);

    termios options;
    tcgetattr(fd_, &options);
    cfsetispeed(&options, B115200);
    cfsetospeed(&options, B115200);

    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;
    options.c_cflag |= (CLOCAL | CREAD);
    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    options.c_oflag &= ~OPOST;

    tcsetattr(fd_, TCSANOW, &options);
    return true;
#endif
}

void EspFlasher::close_port() {
#if defined(_WIN32)
    if (handle_ != INVALID_HANDLE_VALUE) {
        CloseHandle(handle_);
        handle_ = INVALID_HANDLE_VALUE;
    }
#else
    if (fd_ >= 0) {
        close(fd_);
        fd_ = -1;
    }
#endif
}

void EspFlasher::set_dtr(bool state) {
#if defined(_WIN32)
    if (handle_ != INVALID_HANDLE_VALUE) {
        EscapeCommFunction(handle_, state ? SETDTR : CLRDTR);
    }
#else
    if (fd_ >= 0) {
        int status;
        ioctl(fd_, TIOCMGET, &status);
        if (state) status |= TIOCM_DTR;
        else status &= ~TIOCM_DTR;
        ioctl(fd_, TIOCMSET, &status);
    }
#endif
}

void EspFlasher::set_rts(bool state) {
#if defined(_WIN32)
    if (handle_ != INVALID_HANDLE_VALUE) {
        EscapeCommFunction(handle_, state ? SETRTS : CLRRTS);
    }
#else
    if (fd_ >= 0) {
        int status;
        ioctl(fd_, TIOCMGET, &status);
        if (state) status |= TIOCM_RTS;
        else status &= ~TIOCM_RTS;
        ioctl(fd_, TIOCMSET, &status);
    }
#endif
}

bool EspFlasher::write_raw(const uint8_t* data, size_t size) {
#if defined(_WIN32)
    DWORD written = 0;
    return WriteFile(handle_, data, static_cast<DWORD>(size), &written, NULL) && written == size;
#else
    ssize_t res = write(fd_, data, size);
    return res > 0 && static_cast<size_t>(res) == size;
#endif
}

bool EspFlasher::read_raw(uint8_t* buffer, size_t size, uint32_t timeout_ms) {
    auto start = std::chrono::steady_clock::now();
    size_t read_bytes = 0;

    while (read_bytes < size) {
        auto now = std::chrono::steady_clock::now();
        if (std::chrono::duration_cast<std::chrono::milliseconds>(now - start).count() > timeout_ms) {
            return false;
        }

#if defined(_WIN32)
        DWORD read_now = 0;
        if (ReadFile(handle_, buffer + read_bytes, static_cast<DWORD>(size - read_bytes), &read_now, NULL) && read_now > 0) {
            read_bytes += read_now;
        }
#else
        ssize_t res = read(fd_, buffer + read_bytes, size - read_bytes);
        if (res > 0) {
            read_bytes += res;
        }
#endif
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
    return true;
}

// Послідовність автоскидання nodemcu (DTR -> RTS -> RESET)
bool EspFlasher::reset_to_bootloader() {
    set_dtr(false);
    set_rts(true);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    set_dtr(true);
    set_rts(false);
    std::this_thread::sleep_for(std::chrono::milliseconds(500));

    set_dtr(false);
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    return true;
}

std::vector<uint8_t> EspFlasher::make_command_packet(uint8_t op, const std::vector<uint8_t>& payload, uint32_t checksum) {
    std::vector<uint8_t> pkt;
    pkt.push_back(0xC0); // Початок SLIP кадру
    pkt.push_back(0x00); // Direction (0 = request)
    pkt.push_back(op);
    
    uint16_t len = static_cast<uint16_t>(payload.size());
    pkt.push_back(len & 0xFF);
    pkt.push_back((len >> 8) & 0xFF);

    pkt.push_back(checksum & 0xFF);
    pkt.push_back((checksum >> 8) & 0xFF);
    pkt.push_back((checksum >> 16) & 0xFF);
    pkt.push_back((checksum >> 24) & 0xFF);

    for (uint8_t b : payload) {
        if (b == 0xC0) {
            pkt.push_back(0xDB);
            pkt.push_back(0xDC);
        } else if (b == 0xDB) {
            pkt.push_back(0xDB);
            pkt.push_back(0xDD);
        } else {
            pkt.push_back(b);
        }
    }
    pkt.push_back(0xC0); // Кінець SLIP кадру
    return pkt;
}

bool EspFlasher::sync_bootloader(int max_attempts) {
    reset_to_bootloader();
    
    std::vector<uint8_t> sync_payload(36, 0x55);
    sync_payload[0] = 0x07;
    sync_payload[1] = 0x07;
    sync_payload[2] = 0x12;
    sync_payload[3] = 0x20;

    auto sync_pkt = make_command_packet(0x08, sync_payload);

    for (int i = 0; i < max_attempts; ++i) {
        if (write_raw(sync_pkt.data(), sync_pkt.size())) {
            uint8_t response[16];
            if (read_raw(response, 16, 200)) {
                return true;
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    return false;
}

bool EspFlasher::write_flash(uint32_t address, const std::vector<uint8_t>& data, uint32_t block_size) {
    uint32_t total_size = static_cast<uint32_t>(data.size());
    uint32_t num_blocks = (total_size + block_size - 1) / block_size;

    std::cout << "[INFO] Старт запису пам'яті за адресою 0x" << std::hex << address << std::dec << "..." << std::endl;

    for (uint32_t i = 0; i < num_blocks; ++i) {
        uint32_t offset = i * block_size;
        uint32_t current_len = std::min(block_size, total_size - offset);

        std::vector<uint8_t> block_data(data.begin() + offset, data.begin() + offset + current_len);
        
        // Обчислення простої суми байтів блоку
        uint32_t checksum = 0xEF;
        for (uint8_t b : block_data) {
            checksum ^= b;
        }

        auto pkt = make_command_packet(0x03, block_data, checksum);
        if (!write_raw(pkt.data(), pkt.size())) {
            std::cerr << "[ERROR] Збій передачі блоку #" << i << std::endl;
            return false;
        }

        uint8_t ack[10];
        if (!read_raw(ack, 10, 500)) {
            std::cerr << "[ERROR] Таймаут підтвердження блоку #" << i << std::endl;
            return false;
        }

        float progress = static_cast<float>(i + 1) / num_blocks * 100.0f;
        std::cout << "\r[PROGRESS] Записано: " << static_cast<int>(progress) << "% (" << (i + 1) << "/" << num_blocks << " блоків)" << std::flush;
    }
    std::cout << std::endl << "[SUCCESS] Флешування успішно завершено!" << std::endl;
    return true;
}
