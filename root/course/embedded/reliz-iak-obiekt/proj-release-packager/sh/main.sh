# Приклад кроку підписання в релізному конвеєрі CI
- name: Package and Sign Firmware Release
  env:
    SIGNING_KEY_SECRET: ${{ secrets.PROD_RELEASE_ED25519_KEY }}
  run: |
    echo "$SIGNING_KEY_SECRET" > /tmp/release_key.priv
    python3 scripts/firmware_packager.py \
      --payload build/firmware.bin \
      --key /tmp/release_key.priv \
      --out dist/sensor_v1.4.0.fwpkg \
      --hw-id 0x0000A1F0 \
      --rev-min 1 \
      --rev-max 3 \
      --ver 1.4.0 \
      --sec-ver 4 \
      --load-addr 0x08020000
    rm -f /tmp/release_key.priv
