"""Міст між брокером MQTT і подієвим циклом сервера."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable

import paho.mqtt.client as mqtt

from .models import CommandRecord, DeviceReport

LOG = logging.getLogger("control-plane.mqtt")

REQ_TOPIC = "devices/{device_id}/cmd/req"
ACK_FILTER = "devices/+/cmd/ack"
STATUS_FILTER = "devices/+/cmd/status"


class MqttLink:
    """Клієнт paho крутиться у власному потоці, тому кожен звіт заліза
    переводимо в подієвий цикл через run_coroutine_threadsafe: чіпати
    об'єкти asyncio з чужого потоку не можна."""

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        on_report: Callable[[DeviceReport], Awaitable[None]],
        host: str = "localhost",
        port: int = 1883,
    ) -> None:
        self._loop = loop
        self._on_report = on_report
        self._host = host
        self._port = port
        self._online = False

        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id="control-plane"
        )
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._client.reconnect_delay_set(min_delay=1, max_delay=30)

    # --- життєвий цикл ----------------------------------------------------

    def start(self) -> None:
        # connect_async не падає, якщо брокер ще не піднявся: цикл сам
        # ретраїтиме, а поштова скринька тим часом працює через HTTP.
        self._client.connect_async(self._host, self._port, keepalive=30)
        self._client.loop_start()

    def stop(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()

    @property
    def online(self) -> bool:
        return self._online

    # --- вихід ------------------------------------------------------------

    def publish_command(self, record: CommandRecord) -> bool:
        """QoS 1: брокер повторює кадр, доки не отримає PUBACK."""
        payload = json.dumps(
            {
                "cmd_id": record.cmd_id,
                "op": record.op,
                "target_pct": record.params.get("target_pct"),
                "issued_at": int(record.issued_at),
                "ttl_sec": record.ttl_sec,
            },
            ensure_ascii=False,
        )
        info = self._client.publish(
            REQ_TOPIC.format(device_id=record.device_id), payload, qos=1
        )
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            LOG.warning("наказ %s не пішов у брокер (rc=%s)", record.cmd_id, info.rc)
            return False
        return True

    # --- колбеки paho (чужий потік!) --------------------------------------

    def _on_connect(self, client, userdata, flags, reason_code, properties=None) -> None:
        if reason_code != 0:
            LOG.error("брокер відмовив: %s", reason_code)
            return
        self._online = True
        client.subscribe([(ACK_FILTER, 1), (STATUS_FILTER, 1)])
        LOG.info("підписалися на квитанції й звіти вузлів")

    def _on_disconnect(self, client, userdata, flags=None, reason_code=None, properties=None) -> None:
        self._online = False
        LOG.warning("зв'язок із брокером втрачено: %s", reason_code)

    def _on_message(self, client, userdata, message: mqtt.MQTTMessage) -> None:
        try:
            report = DeviceReport.from_payload(message.payload)
        except (ValueError, TypeError) as exc:
            LOG.warning("непридатний кадр у %s: %s", message.topic, exc)
            return
        try:
            asyncio.run_coroutine_threadsafe(self._on_report(report), self._loop)
        except RuntimeError:
            LOG.warning("подієвий цикл уже зупинено, звіт %s втрачено", report.cmd_id)
