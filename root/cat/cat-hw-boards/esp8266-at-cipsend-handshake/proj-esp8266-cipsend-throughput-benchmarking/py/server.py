import socket
import time
import struct

HOST = '0.0.0.0'
PORT = 8080
CHUNK_SIZE = 1024  # Очікуваний розмір блоку від ESP8266

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Сервер слухає на {HOST}:{PORT}...")
        
        while True:
            conn, addr = s.accept()
            print(f"З'єднання з {addr}")
            handle_client(conn)
            print("Клієнт відключився")

def handle_client(conn):
    with conn:
        buffer = bytearray()
        total_bytes = 0
        expected_seq = 0
        start_time = time.time()
        last_report_time = start_time
        bytes_since_report = 0
        
        while True:
            data = conn.recv(4096)
            if not data:
                break
            
            buffer.extend(data)
            
            # Обробляємо повні блоки даних
            while len(buffer) >= CHUNK_SIZE:
                chunk = buffer[:CHUNK_SIZE]
                del buffer[:CHUNK_SIZE]
                
                # Перевірка контрольної суми (останній байт — XOR усіх попередніх)
                calculated_checksum = 0
                for byte in chunk[:-1]:
                    calculated_checksum ^= byte
                
                received_checksum = chunk[-1]
                if calculated_checksum != received_checksum:
                    print(f"Помилка КС! Очікувано: {calculated_checksum}, Отримано: {received_checksum}")
                
                # Перші 4 байти — номер пакету (little-endian)
                seq = struct.unpack('<I', chunk[:4])[0]
                if seq != expected_seq:
                    print(f"Втрата пакетів! Очікуваний seq: {expected_seq}, Отриманий: {seq}")
                    expected_seq = seq
                
                expected_seq += 1
                total_bytes += CHUNK_SIZE
                bytes_since_report += CHUNK_SIZE
                
                current_time = time.time()
                if current_time - last_report_time >= 1.0:
                    speed_kb = (bytes_since_report / 1024) / (current_time - last_report_time)
                    print(f"Отримано: {total_bytes / 1024:.2f} KB, Швидкість: {speed_kb:.2f} KB/s")
                    last_report_time = current_time
                    bytes_since_report = 0

if __name__ == "__main__":
    start_server()
