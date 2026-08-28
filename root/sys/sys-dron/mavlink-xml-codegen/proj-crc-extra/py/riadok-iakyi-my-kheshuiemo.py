# -*- coding: utf-8 -*-
"""CRC_EXTRA з опису MAVLink. Лише стандартна бібліотека."""
import sys
import xml.etree.ElementTree as ET

# розмір ОДНОГО елемента типу — саме він є ключем сортування
ELEM_SIZE = {
    'char': 1, 'int8_t': 1, 'uint8_t': 1,
    'int16_t': 2, 'uint16_t': 2,
    'int32_t': 4, 'uint32_t': 4, 'float': 4,
    'int64_t': 8, 'uint64_t': 8, 'double': 8,
}

class Field:
    def __init__(self, type_attr, name):
        t, self.count = type_attr, 0
        if t == 'uint8_t_mavlink_version':     # псевдотип: на дроті це просто байт
            t = 'uint8_t'
        i = t.find('[')
        if i != -1:                            # масив: char[50] → char + count 50
            self.count = int(t[i + 1:-1])
            t = t[:i]
            if t == 'array':                   # застарілий псевдотип зі старих описів
                t = 'int8_t'
        self.type, self.name = t, name
        self.elem = ELEM_SIZE[t]

def read_message(msg_el):
    """Базові поля повідомлення — усе до тега <extensions/>."""
    base, after_tag = [], False
    for el in msg_el:
        if el.tag == 'extensions':
            after_tag = True
        elif el.tag == 'field' and not after_tag:
            base.append(Field(el.get('type'), el.get('name')))
    return base

def wire_order(fields):
    """Більші типи вперед; рівні лишаються в порядку XML — sorted стійкий."""
    return sorted(fields, key=lambda f: f.elem, reverse=True)

def signature(name, base):
    """Той самий рядок, який хешує генератор. Пробіл — після КОЖНОГО слова."""
    buf = bytearray((name + ' ').encode('ascii'))
    for f in wire_order(base):
        buf += (f.type + ' ').encode('ascii')
        buf += (f.name + ' ').encode('ascii')
        if f.count:
            buf.append(f.count)                # сирий байт, не десятковий запис
    return buf

def crc_extra(name, base):
    crc = crc16_bitwise(signature(name, base))
    return (crc & 0xFF) ^ (crc >> 8)           # згортання двох байтів в один

def scan(path):
    root = ET.parse(path).getroot()
    return {m.get('name'): (int(m.get('id')), crc_extra(m.get('name'), read_message(m)))
            for m in root.iter('message')}

if __name__ == '__main__':
    for name, (mid, extra) in sorted(scan(sys.argv[1]).items(), key=lambda kv: kv[1][0]):
        print('%-14s id=%-5d CRC_EXTRA=%d' % (name, mid, extra))
