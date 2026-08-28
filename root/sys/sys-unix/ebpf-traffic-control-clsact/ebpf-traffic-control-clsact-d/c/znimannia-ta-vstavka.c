// Витягування тунельного ключа (VNI) на вхідному шляху
struct bpf_tunnel_key key = {};
int err = bpf_skb_get_tunnel_key(skb, &key, sizeof(key), 0);
if (!err) {
    // key.tunnel_id містить VNI (Virtual Network Identifier)
    // key.remote_ipv4 містить зовнішню IP-адресу хоста-відправника
}

// Налаштування інкапсуляції для вихідного пакета
struct bpf_tunnel_key out_key = {};
out_key.tunnel_id = 100;                // VXLAN VNI 100
out_key.remote_ipv4 = bpf_htonl(0x0A010101); // 10.1.1.1
out_key.tunnel_ttl = 64;

bpf_skb_set_tunnel_key(skb, &out_key, sizeof(out_key), BPF_F_ZERO_CSUM_TX);
