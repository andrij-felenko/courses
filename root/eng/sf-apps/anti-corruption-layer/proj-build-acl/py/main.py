# main.py — composition root. Поза доменом. Єдине місце, що бачить обидва світи.
import os
from crm.http_client import CrmHttpClient
from acl.crm_facade import CrmOrderFacade
from acl.crm_order_source import CrmOrderSource
from domain.order_service import OrderService

http    = CrmHttpClient(os.environ["CRM_URL"])
facade  = CrmOrderFacade(http)
source  = CrmOrderSource(facade)    # ← ось де CRM стає OrderSource
service = OrderService(source)      # домен бачить лише порт

service.process_batch()
