import sigrokdecode as srd

class Decoder(srd.Decoder):
    api_version = 3
    id = 'custom_uart'
    name = 'Custom UART'
    longname = 'Custom UART Protocol Decoder'
    desc = 'Decodes custom UART packets.'
    license = 'gplv3+'
    inputs = ['logic']
    outputs = ['custom_uart']
    tags = ['Embedded']
    
    channels = (
        {'id': 'rx', 'name': 'RX', 'desc': 'Receive Line'},
    )
    options = (
        {'id': 'baudrate', 'desc': 'Baud rate', 'default': 115200},
    )
    annotations = (
        ('byte', 'Decoded Byte'),
        ('error', 'Framing Error'),
    )
    annotation_rows = (
        ('bytes', 'Bytes', (0, 1)),
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.samplenum = 0

    def start(self):
        self.out_python = self.register(srd.OUTPUT_PYTHON)
        self.out_ann = self.register(srd.OUTPUT_ANN)
