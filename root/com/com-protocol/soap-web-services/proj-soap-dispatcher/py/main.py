import re
from typing import Dict, Any, Tuple, Optional

class SoapDispatcher:
    def __init__(self, version: str = "1.1"):
        self.version = version

    def dispatch(self, method: str, content_type: str, body: str) -> Tuple[int, Dict[str, str], str]:
        # Перевірка HTTP методу
        if method != "POST":
            return 405, {"Content-Type": "text/plain; charset=utf-8"}, "Вимагається HTTP POST"

        # 1. Валідація заголовка Content-Type
        if self.version == "1.1" and not content_type.startswith("text/xml"):
            return self._build_fault("soap:Client", "Очікується text/xml для SOAP 1.1", "INVALID_CONTENT_TYPE", 415)
        elif self.version == "1.2" and not content_type.startswith("application/soap+xml"):
            return self._build_fault("soap12:Sender", "Очікується application/soap+xml для SOAP 1.2", "INVALID_CONTENT_TYPE", 415)

        # 2. Перевірка базової структури
        if "<Envelope" not in body or "<Body" not in body:
            return self._build_fault("soap:Client", "Відсутній конверт або тіло повідомлення", "MALFORMED_XML", 400)

        # 3. Перевірка блоків mustUnderstand
        header_match = re.search(r"<(?:\w+:)?Header>(.*?)</(?:\w+:)?Header>", body, re.DOTALL)
        if header_match:
            header_content = header_match.group(1)
            mu_blocks = re.findall(r"<(\w+:[a-zA-Z0-9_]+)[^>]*mustUnderstand\s*=\s*[\"'](1|true)[\"'][^>]*>", header_content)
            for tag, _ in mu_blocks:
                if "Security" not in tag:
                    return self._build_fault("soap:MustUnderstand", f"Непідтримуваний обов'язковий заголовок: {tag}", "MANDATORY_HEADER_FAILED", 500)

        # 4. Витягування аргументів платежу
        acc = self._extract_tag(body, "accountNumber")
        amt = self._extract_tag(body, "amount")
        curr = self._extract_tag(body, "currency")

        if not acc or not amt or not curr:
            return self._build_fault("soap:Client", "Відсутні обов'язкові параметри accountNumber, amount або currency", "MISSING_FIELDS", 500 if self.version == "1.1" else 400)

        try:
            amount_val = float(amt)
            if amount_val <= 0:
                raise ValueError()
        except ValueError:
            return self._build_fault("soap:Client", "Сума платежу повинна бути додатним числом", "INVALID_AMOUNT", 500 if self.version == "1.1" else 400)

        # 5. Успішна відповідь
        return self._build_success("TX-PY-2026-8812", "SUCCESS", "2026-08-20T10:30:00Z")

    def _extract_tag(self, xml: str, tag: str) -> Optional[str]:
        m = re.search(rf"<(?:\w+:)?{tag}>([^<]*)</(?:\w+:)?{tag}>", xml)
        return m.group(1).strip() if m else None

    def _build_success(self, tx_id: str, status: str, ts: str) -> Tuple[int, Dict[str, str], str]:
        xml = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:m="http://bank.example.com/payments">
  <soap:Body>
    <m:ProcessPaymentResponse>
      <m:transactionId>{tx_id}</m:transactionId>
      <m:status>{status}</m:status>
      <m:timestamp>{ts}</m:timestamp>
    </m:ProcessPaymentResponse>
  </soap:Body>
</soap:Envelope>"""
        return 200, {"Content-Type": "text/xml; charset=utf-8"}, xml

    def _build_fault(self, code: str, reason: str, err_code: str, status_code: int) -> Tuple[int, Dict[str, str], str]:
        xml = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <soap:Fault>
      <faultcode>{code}</faultcode>
      <faultstring>{reason}</faultstring>
      <detail>
        <err:PaymentFault xmlns:err="http://bank.example.com/errors">
          <err:errorCode>{err_code}</err:errorCode>
        </err:PaymentFault>
      </detail>
    </soap:Fault>
  </soap:Body>
</soap:Envelope>"""
        return status_code, {"Content-Type": "text/xml; charset=utf-8"}, xml
