import xml.etree.ElementTree as ET
from defusedxml import DefusedXmlException
import defusedxml.ElementTree as DefusedET

class StreamSummary:
    def __init__(self):
        self.total_uah = 0.0
        self.total_usd = 0.0
        self.count = 0

def parse_stream_streaming_py(filepath: str) -> StreamSummary:
    summary = StreamSummary()
    
    # Використовуємо iterparse для потокового читання подій 'end'
    # Це дозволяє видаляти оброблені елементи з пам'яті
    context = ET.iterparse(filepath, events=("start", "end"))
    _, root = next(context)  # Отримуємо посилання на кореневий елемент
    
    for event, elem in context:
        if event == "end" and elem.tag == "tx":
            if elem.get("status") == "completed":
                amount_elem = elem.find("amount")
                if amount_elem is not None and amount_elem.text:
                    currency = amount_elem.get("currency")
                    val = float(amount_elem.text.strip())
                    if currency == "UAH":
                        summary.total_uah += val
                    elif currency == "USD":
                        summary.total_usd += val
                    summary.count += 1
            
            # КРИТИЧНО ДЛЯ ПАМ'ЯТІ O(1):
            # Очищуємо вузол та видаляємо його з батьківського кореня
            elem.clear()
            root.clear()
            
    return summary
