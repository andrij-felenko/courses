    # Розпаковані канали й статистика тримаємо на самому парсері (self):
    #   self.channels — список із 16 каналів; self.link — dict зі статистикою.
    #   (ініціалізуються в __init__: self.channels = [0]*16; self.link = {})

    # frame = bytes(тип, дані..., CRC); len == len(frame) (тип+дані+CRC).
    def dispatch(self, frame):
        type_    = frame[0]
        payload  = frame[1:-1]          # одразу після типу, без CRC

        if type_ == CRSF_TYPE_RC_CHANNELS_PACKED:
            # Рівно 16×11 біт = 22 байти. Інша довжина — не наш кадр, ігноруємо.
            if len(payload) == 22:
                self.unpack_channels(payload)

        elif type_ == CRSF_TYPE_LINK_STATISTICS:
            if len(payload) == 10:
                self.parse_link(payload)

        # else: GPS (0x02), батарея (0x08), режим польоту… — тут не розбираємо.
