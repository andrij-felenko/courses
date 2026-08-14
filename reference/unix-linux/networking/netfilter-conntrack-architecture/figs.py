import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_conntrack_architecture():
    w, h = 840, 360
    frags = []
    
    frags.append(fitbox(30, 80, 180, 220, "Клієнт (Host A)\nIP: 192.168.1.100\nPort: 50000", size=13, fill="#e8f4f8", stroke="#2457d6"))
    frags.append(fitbox(260, 60, 320, 260, "Підсистема nf_conntrack\n(Запис struct nf_conn)\n \nORIGINAL Tuple:\nSRC=192.168.1.100 DST=8.8.8.8\nSPORT=50000 DPORT=80 PROTO=TCP\n \nREPLY Tuple:\nSRC=8.8.8.8 DST=192.168.1.100\nSPORT=80 DPORT=50000 PROTO=TCP", size=12, fill="#fef9e7", stroke="#d35400"))
    frags.append(fitbox(630, 80, 180, 220, "Сервер (Host B)\nIP: 8.8.8.8\nPort: 80", size=13, fill="#fdedec", stroke="#c0392b"))
    
    frags.append(arrow(210, 130, 260, 130, color="#2457d6", sw=2))
    frags.append(arrow(580, 130, 630, 130, color="#2457d6", sw=2))
    frags.append(text(235, 115, "Пакет (SYN)", size=11, color="#2457d6"))
    frags.append(text(605, 115, "Пакет (SYN)", size=11, color="#2457d6"))
    
    frags.append(arrow(630, 230, 580, 230, color="#c0392b", sw=2))
    frags.append(arrow(260, 230, 210, 230, color="#c0392b", sw=2))
    frags.append(text(605, 245, "Відповідь (SYN-ACK)", size=11, color="#c0392b"))
    frags.append(text(235, 245, "Відповідь (SYN-ACK)", size=11, color="#c0392b"))

    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, 'conntrack-architecture.svg'), w, h, *frags, title="Архітектура Tuples у nf_conntrack (ORIGINAL і REPLY)")

def build_conntrack_hooks():
    w, h = 900, 380
    frags = []
    
    frags.append(fitbox(20, 140, 110, 80, "Вхідний пакет\n(NIC rx)", size=12, fill="#eaedd9", stroke="#27ae60"))
    frags.append(fitbox(160, 100, 150, 160, "NF_INET_PRE_ROUTING\n \n1. raw (NOTRACK)\n2. conntrack (in)\n3. mangle\n4. nat (PREROUTING)", size=11, fill="#f4f6f8", stroke="#1a1a1a"))
    frags.append(fitbox(340, 140, 110, 80, "Рішення про\nмаршрут\n(Routing)", size=11, fill="#e8f4f8", stroke="#2457d6"))
    frags.append(fitbox(480, 60, 150, 100, "NF_INET_FORWARD\n \n1. mangle\n2. filter", size=11, fill="#f4f6f8", stroke="#1a1a1a"))
    frags.append(fitbox(480, 200, 150, 100, "NF_INET_LOCAL_IN\n \n1. filter\n2. mangle\n3. nat (INPUT)", size=11, fill="#f4f6f8", stroke="#1a1a1a"))
    frags.append(fitbox(660, 100, 150, 160, "NF_INET_POST_ROUTING\n \n1. mangle\n2. nat (POSTROUTING)\n3. conntrack (confirm)", size=11, fill="#fdedec", stroke="#c0392b"))
    frags.append(fitbox(830, 140, 60, 80, "Вихід\n(NIC tx)", size=11, fill="#eaedd9", stroke="#27ae60"))
    
    frags.append(arrow(130, 180, 160, 180, sw=2))
    frags.append(arrow(310, 180, 340, 180, sw=2))
    frags.append(arrow(450, 160, 480, 110, sw=1.5))
    frags.append(arrow(450, 200, 480, 250, sw=1.5))
    frags.append(arrow(630, 110, 660, 160, sw=1.5))
    frags.append(arrow(810, 180, 830, 180, sw=2))

    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, 'conntrack-hooks-flow.svg'), w, h, *frags, title="Проходження пакета через хуки Netfilter та точки входу Conntrack")

def build_conntrack_hashtable():
    w, h = 860, 360
    frags = []
    
    frags.append(fitbox(20, 120, 160, 120, "skb (Пакет)\n \nОбчислення хешу:\nSipHash(Tuple, key)\n% HASHSIZE", size=11, fill="#e8f4f8", stroke="#2457d6"))
    frags.append(fitbox(220, 60, 140, 240, "Хеш-таблиця\n(Buckets Array)\n \nBucket [0]\nBucket [1] --->\nBucket [2]\n...\nBucket [N-1]", size=11, fill="#f4f6f8", stroke="#1a1a1a"))
    frags.append(fitbox(400, 70, 200, 100, "nf_conntrack_tuple_hash\n[ORIGINAL]\nhlist_nulls_node\nTuple: 192.168.1.10->8.8.8.8", size=10, fill="#fef9e7", stroke="#d35400"))
    frags.append(fitbox(640, 50, 200, 260, "struct nf_conn\n(Slab: nf_conntrack)\n \n• tuplehash[ORIGINAL]\n• tuplehash[REPLY]\n• status (IPS_ASSURED...)\n• timeout (timer_list)\n• master (helper)\n• extensions (NAT, mark)", size=10, fill="#eaedd9", stroke="#27ae60"))
    frags.append(fitbox(400, 200, 200, 100, "nf_conntrack_tuple_hash\n[REPLY]\nhlist_nulls_node\nTuple: 8.8.8.8->192.168.1.10", size=10, fill="#fdedec", stroke="#c0392b"))
    
    frags.append(arrow(180, 180, 220, 180, sw=2))
    frags.append(arrow(360, 110, 400, 110, sw=1.5))
    frags.append(arrow(600, 120, 640, 120, sw=1.5))
    frags.append(arrow(600, 230, 640, 230, sw=1.5))
    frags.append(line(400, 170, 400, 200, color="#6b7280", dash="3,3"))

    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, 'conntrack-hashtable-struct.svg'), w, h, *frags, title="Структура conntrack table в пам'яті ядра та зв'язок із struct nf_conn")

if __name__ == '__main__':
    build_conntrack_architecture()
    build_conntrack_hooks()
    build_conntrack_hashtable()
