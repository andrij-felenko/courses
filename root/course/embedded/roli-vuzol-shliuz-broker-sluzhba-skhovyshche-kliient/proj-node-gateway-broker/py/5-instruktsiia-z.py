   import socket, struct, time

   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   # Формуємо валідний бінарний кадр для Node 42
   # Magic=0xAA, Type=1, Node=42, Seq=1, Temp=2340 (23.40 C), Bat=3300mV, Flags=0, Res=0
   data_without_crc = struct.pack("<BBHIhHBB", 0xAA, 0x01, 42, 1, 2340, 3300, 0, 0)
   
   crc = 0xFFFF
   for b in data_without_crc:
       crc ^= b << 8
       for _ in range(8):
           crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF

   packet = data_without_crc + struct.pack("<H", crc)
   sock.sendto(packet, ("127.0.0.1", 9000))
   print("Кадр відправлено успішно!")
