from typing import List, Dict, Any

class ContentDefinedChunker:
    BASE: int = 257
    MOD: int = 10**9 + 7

    @classmethod
    def chunk_data(cls, data: bytes, window_size: int = 16, target_chunk_size: int = 64) -> List[Dict[str, Any]]:
        n = len(data)
        if n == 0:
            return []

        mask = target_chunk_size - 1
        E = pow(cls.BASE, window_size - 1, cls.MOD)

        chunks = []
        current_hash = 0
        chunk_start = 0

        for i in range(n):
            if i < window_size:
                current_hash = (current_hash * cls.BASE + data[i]) % cls.MOD
            else:
                leading = data[i - window_size]
                trailing = data[i]:

                # Формула ковзного зсуву
                current_hash = (current_hash - leading * E) % cls.MOD
                current_hash = (current_hash * cls.BASE + trailing) % cls.MOD

            current_len = i - chunk_start + 1
            is_boundary = (i >= window_size - 1) and ((current_hash & mask) == 0)
            is_max_size = (current_len >= target_chunk_size * 4)

            if is_boundary or is_max_size or (i == n - 1):
                chunks.append({
                    "start_offset": chunk_start,
                    "length": current_len,
                    "hash": current_hash
                })
                chunk_start = i + 1

        return chunks

# Демонстрація CDC чанкінгу
if __name__ == "__main__":
    test_stream = bytes([(i * 13 + 7) % 256 for i in range(512)])
    result_chunks = ContentDefinedChunker.chunk_data(test_stream, window_size=16, target_chunk_size=64)

    print(f"Згенеровано {len(result_chunks)} динамічних блоків (CDC):")
    print("-" * 56)
    print("№   | Зсув (байтів) | Довжина (байтів) | Хеш межі")
    print("-" * 56)
    for idx, c in enumerate(result_chunks, 1):
        print(f"{idx:3d} | {c['start_offset']:13d} | {c['length']:16d} | 0x{c['hash']:x}")
