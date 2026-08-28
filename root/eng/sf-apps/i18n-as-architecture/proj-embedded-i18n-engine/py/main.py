#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n_pack.py — Офлайн-пакувальник ресурсів у двійковий образ .emb_i18n
Вирівнювання на 4 байти, дедуплікація пулу рядків, MurmurHash3_32.
"""
import sys
import json
import struct

def murmurhash3_32(key: str, seed: int = 0x9747b28c) -> int:
    data = key.encode('utf-8')
    h = seed
    for b in data:
        k = b
        k = (k * 0xcc9e2d51) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * 0x1b873593) & 0xFFFFFFFF
        h ^= k
        h = ((h << 13) | (h >> 19)) & 0xFFFFFFFF
        h = (h * 5 + 0xe6546b64) & 0xFFFFFFFF
    
    h ^= len(data)
    h = (h ^ (h >> 16)) & 0xFFFFFFFF
    h = (h * 0x85ebca6b) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) & 0xFFFFFFFF
    h = (h * 0xc2b2ae35) & 0xFFFFFFFF
    h = (h ^ (h >> 16)) & 0xFFFFFFFF
    return h

def align4(data: bytearray) -> None:
    while len(data) % 4 != 0:
        data.append(0)

def build_binary_image(locales_config: list) -> bytes:
    image = bytearray()
    
    # 1. Зарезервувати заголовок (32 байти)
    header_format = "<IIHHIIII"
    image.extend(b'\x00' * 32)
    
    locale_count = len(locales_config)
    locale_table_offset = len(image)
    
    # Резервуємо місце під таблицю дескрипторів локалей (20 байтів на запис)
    loc_table_bytes = locale_count * 20
    image.extend(b'\x00' * loc_table_bytes)
    align4(image)
    
    locale_descriptors = []
    
    for loc in locales_config:
        loc_id = murmurhash3_32(loc["id_str"])
        rule_id = loc.get("plural_rule_id", 1)
        is_rtl = 1 if loc.get("is_rtl", False) else 0
        
        messages = loc["messages"]
        msg_keys = sorted(messages.keys(), key=lambda k: murmurhash3_32(k))
        
        string_pool = bytearray()
        string_map = {}
        
        def add_string(s: str) -> int:
            if s in string_map:
                return string_map[s]
            off = len(string_pool)
            encoded = s.encode('utf-8') + b'\x00'
            string_pool.extend(encoded)
            string_map[s] = off
            return off
        
        descriptors_data = bytearray()
        index_entries = []
        
        desc_start_offset = len(image)
        
        for k in msg_keys:
            val = messages[k]
            khash = murmurhash3_32(k)
            
            curr_desc_off = desc_start_offset + len(descriptors_data)
            index_entries.append((khash, curr_desc_off))
            
            if isinstance(val, str):
                s_off = add_string(val)
                desc_bytes = struct.pack("<BBH 6I", 0, 0, 1, s_off, 0, 0, 0, 0, 0)
                descriptors_data.extend(desc_bytes)
            elif isinstance(val, dict):
                cats = ["zero", "one", "two", "few", "many", "other"]
                offsets = [add_string(val[c]) if c in val else 0 for c in cats]
                desc_bytes = struct.pack("<BBH 6I", 1, 0, 6, *offsets)
                descriptors_data.extend(desc_bytes)
        
        align4(descriptors_data)
        image.extend(descriptors_data)
        
        index_table_offset = len(image)
        for khash, doff in index_entries:
            image.extend(struct.pack("<II", khash, doff))
        align4(image)
        
        string_pool_offset = len(image)
        image.extend(string_pool)
        align4(image)
        
        locale_descriptors.append({
            "locale_id": loc_id,
            "plural_rule_id": rule_id,
            "flags": is_rtl,
            "message_count": len(msg_keys),
            "index_table_offset": index_table_offset,
            "string_pool_offset": string_pool_offset
        })
    
    for i, ld in enumerate(locale_descriptors):
        packed_ld = struct.pack("<IHHI II", 
                                ld["locale_id"],
                                ld["plural_rule_id"],
                                ld["flags"],
                                ld["message_count"],
                                ld["index_table_offset"],
                                ld["string_pool_offset"])
        pos = locale_table_offset + i * 20
        image[pos:pos+20] = packed_ld
    
    total_size = len(image)
    hdr_bytes = struct.pack(header_format,
                            0x45493138, # Magic 'EI18'
                            1,          # Version
                            0,          # Flags
                            locale_count,
                            locale_table_offset,
                            total_size,
                            0,          # CRC32
                            0)          # Reserved
    image[0:32] = hdr_bytes
    return bytes(image)

if __name__ == "__main__":
    sample_config = [
        {
            "id_str": "uk-UA",
            "plural_rule_id": 2,
            "is_rtl": False,
            "messages": {
                "system.ready": "Система готова до роботи",
                "sensor.temp": "Температура: {0} C",
                "storage.deleted": {
                    "one": "Вилучено {0} файл",
                    "few": "Вилучено {0} файли",
                    "many": "Вилучено {0} файлів",
                    "other": "Вилучено {0} файлу"
                }
            }
        },
        {
            "id_str": "en-US",
            "plural_rule_id": 1,
            "is_rtl": False,
            "messages": {
                "system.ready": "System is ready",
                "sensor.temp": "Temperature: {0} C",
                "storage.deleted": {
                    "one": "{0} file deleted",
                    "other": "{0} files deleted"
                }
            }
        }
    ]
    blob = build_binary_image(sample_config)
    with open("locales.bin", "wb") as f:
        f.write(blob)
    print(f"Згенеровано двійковий образ locales.bin ({len(blob)} байтів).")
