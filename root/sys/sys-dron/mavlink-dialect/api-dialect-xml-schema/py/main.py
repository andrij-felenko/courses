import xml.etree.ElementTree as ET
import os
import sys

def validate_dialect(xml_path, seen_ids=None, visited_files=None):
    if seen_ids is None:
        seen_ids = {}
    if visited_files is None:
        visited_files = set()

    real_path = os.path.abspath(xml_path)
    if real_path in visited_files:
        return seen_ids
    visited_files.add(real_path)

    tree = ET.parse(real_path)
    root = tree.getroot()

    if root.tag != 'mavlink':
        raise ValueError(f"Кореневий тег повинен бути <mavlink>, знайдено <{root.tag}>")

    base_dir = os.path.dirname(real_path)
    for inc in root.findall('include'):
        inc_path = os.path.join(base_dir, inc.text.strip())
        validate_dialect(inc_path, seen_ids, visited_files)

    messages = root.find('messages')
    if messages is not None:
        for msg in messages.findall('message'):
            msg_id = int(msg.attrib['id'])
            msg_name = msg.attrib['name']

            if msg_id in seen_ids:
                prev_name, prev_file = seen_ids[msg_id]
                raise ValueError(
                    f"Колізія Message ID {msg_id}: повідомлення '{msg_name}' у {os.path.basename(real_path)} "
                    f"конфліктує з '{prev_name}' у {os.path.basename(prev_file)}"
                )
            seen_ids[msg_id] = (msg_name, real_path)

    return seen_ids

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Використання: python validate_dialect.py <path_to_dialect.xml>")
        sys.exit(1)
    try:
        all_messages = validate_dialect(sys.argv[1])
        print(f"Успішно перевірено: знайдено {len(all_messages)} унікальних повідомлень.")
    except Exception as e:
        print(f"ПОМИЛКА ВАЛІДАЦІЇ: {e}", file=sys.stderr)
        sys.exit(1)
