"""
WebSocket consumer for real-time pipeline & alert notifications.

Clients connect to:
  ws://<host>/ws/pipeline/<tenant_id>/

They receive JSON messages when:
  - Pipeline segment status changes
  - Tank telemetry updates
  - Alert notifications fire
  - Batch position updates
"""
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('pipeline')


class PipelineConsumer(AsyncWebsocketConsumer):
    """
    Handles per-tenant WebSocket connections for real-time dashboard updates.
    External code (Celery tasks, views) sends updates via channel_layer.group_send().
    """

    async def connect(self):
        self.tenant_id = self.scope['url_route']['kwargs']['tenant_id']
        self.group_name = f'tenant_{self.tenant_id}'

        # Join the tenant-specific group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f'WebSocket connected: tenant={self.tenant_id}')

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f'WebSocket disconnected: tenant={self.tenant_id}')

    async def receive(self, text_data=None, bytes_data=None):
        """Handle messages from the client (e.g., subscription filters)."""
        # For now, we only push data TO clients.
        pass

    async def send_json(self, content):
        """Helper to send JSON-serialized data to the WebSocket."""
        await self.send(text_data=json.dumps(content))

    # ── Handler methods called via channel_layer.group_send() ──

    async def pipeline_update(self, event):
        """Pipeline segment status/telemetry change."""
        await self.send_json({
            'type': 'pipeline_update',
            'data': event['data'],
        })

    async def tank_update(self, event):
        """Tank telemetry update."""
        await self.send_json({
            'type': 'tank_update',
            'data': event['data'],
        })

    async def batch_update(self, event):
        """Batch position / status change."""
        await self.send_json({
            'type': 'batch_update',
            'data': event['data'],
        })

    async def alert_notification(self, event):
        """New alert notification."""
        await self.send_json({
            'type': 'alert_notification',
            'data': event['data'],
        })

    async def vessel_update(self, event):
        """Vessel discharge progress update."""
        await self.send_json({
            'type': 'vessel_update',
            'data': event['data'],
        })
