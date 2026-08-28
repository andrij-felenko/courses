# -*- coding: utf-8 -*-
import os, sys, base64

DIR = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(DIR, 'img')
os.makedirs(IMG, exist_ok=True)

def write_b64(rel_path, b64_str):
    full_path = os.path.join(DIR, rel_path)
    data = base64.b64decode(b64_str.encode('ascii'))
    with open(full_path, 'wb') as f:
        f.write(data)
    text = data.decode('utf-8')
    print(f'Wrote {rel_path}: {len(text.split())} words, {len(data)} bytes')

print('gen_all.py ready')
