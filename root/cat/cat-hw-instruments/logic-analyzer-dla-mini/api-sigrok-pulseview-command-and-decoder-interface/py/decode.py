    def decode(self):
        while True:
            # Очікування спадного фронту старт-біта на каналі 0
            self.wait({0: 'f'})
            start_samplenum = self.samplenum
            
            # Розрахунок зсуву на середину першого біта
            half_bit = int(self.samplerate / self.options['baudrate'] / 2)
            self.wait({'skip': half_bit})
            
            # Потактне зчитування 8 бітів даних
            byte_val = 0
            bit_samples = int(self.samplerate / self.options['baudrate'])
            for i in range(8):
                self.wait({'skip': bit_samples})
                pins = self.matched
                byte_val |= (pins[0] << i)
            
            end_samplenum = self.samplenum
            # Публікація анотацій у графічному інтерфейсі PulseView
            self.put(start_samplenum, end_samplenum, self.out_ann, 
                     [0, [f'0x{byte_val:02X}', f'{byte_val:02X}']])
