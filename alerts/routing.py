"""
WebSocket URL routing for Django Channels.
"""
from django.urls import re_path
from alerts.consumers import PipelineConsumer

websocket_urlpatterns = [
    re_path(r'ws/pipeline/(?P<tenant_id>\d+)/$', PipelineConsumer.as_asgi()),
]
