"""
Notificador assíncrono via HTTP (httpx.AsyncClient), disparado em BackgroundTasks
após operações sensíveis (depósito, saque, transferência). Não bloqueia a resposta
ao cliente e falhas de rede são apenas logadas.
"""
import httpx

from app.core.config import settings
from app.core.logging_config import app_logger


async def notify_webhook(event: str, payload: dict) -> None:
    if not settings.NOTIFICATION_WEBHOOK_URL:
        app_logger.info("Webhook não configurado. Evento '%s' apenas logado: %s", event, payload)
        return

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(settings.NOTIFICATION_WEBHOOK_URL, json={"event": event, "payload": payload})
        app_logger.info("Webhook enviado com sucesso para evento '%s'", event)
    except httpx.HTTPError as exc:
        app_logger.warning("Falha ao enviar webhook para evento '%s': %s", event, exc)
