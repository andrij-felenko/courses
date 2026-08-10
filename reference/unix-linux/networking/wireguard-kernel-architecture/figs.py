#!/usr/bin/env python3
import os

def render():
    svg_arch = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
  <rect width="100%" height="100%" fill="#ffffff" />
  <text x="400" y="40" font-family="sans-serif" font-size="24" text-anchor="middle">WireGuard Architecture</text>
  
  <rect x="50" y="80" width="250" height="250" rx="10" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
  <text x="175" y="110" font-family="sans-serif" font-size="20" font-weight="bold" text-anchor="middle">Kernel Space (Peer A)</text>
  <rect x="70" y="140" width="210" height="80" rx="5" fill="#cce5ff" stroke="#b8daff" stroke-width="2"/>
  <text x="175" y="170" font-family="sans-serif" font-size="16" font-weight="bold" text-anchor="middle">wg0 Interface</text>
  <text x="175" y="195" font-family="sans-serif" font-size="14" text-anchor="middle">Cryptokey Routing</text>
  <text x="175" y="215" font-family="sans-serif" font-size="12" text-anchor="middle">AllowedIPs: 10.0.0.2/32</text>
  
  <rect x="500" y="80" width="250" height="250" rx="10" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
  <text x="625" y="110" font-family="sans-serif" font-size="20" font-weight="bold" text-anchor="middle">Kernel Space (Peer B)</text>
  <rect x="520" y="140" width="210" height="80" rx="5" fill="#d4edda" stroke="#c3e6cb" stroke-width="2"/>
  <text x="625" y="170" font-family="sans-serif" font-size="16" font-weight="bold" text-anchor="middle">wg0 Interface</text>
  <text x="625" y="195" font-family="sans-serif" font-size="14" text-anchor="middle">Cryptokey Routing</text>
  <text x="625" y="215" font-family="sans-serif" font-size="12" text-anchor="middle">AllowedIPs: 10.0.0.1/32</text>
  
  <path d="M 280 180 L 520 180" stroke="#007bff" stroke-width="4" stroke-dasharray="8,4"/>
  <text x="400" y="170" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">UDP Socket</text>
  <text x="400" y="200" font-family="sans-serif" font-size="12" text-anchor="middle">Noise_IK Handshake</text>
  <text x="400" y="215" font-family="sans-serif" font-size="12" text-anchor="middle">ChaCha20-Poly1305</text>
  
  <rect x="70" y="240" width="210" height="60" rx="5" fill="#f8d7da" stroke="#f5c6cb" stroke-width="2"/>
  <text x="175" y="275" font-family="sans-serif" font-size="14" text-anchor="middle">User Space App</text>
  
  <rect x="520" y="240" width="210" height="60" rx="5" fill="#f8d7da" stroke="#f5c6cb" stroke-width="2"/>
  <text x="625" y="275" font-family="sans-serif" font-size="14" text-anchor="middle">User Space App</text>
</svg>"""

    with open("wireguard_arch.svg", "w", encoding="utf-8") as f:
        f.write(svg_arch)

if __name__ == "__main__":
    render()
