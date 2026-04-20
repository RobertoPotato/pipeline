"""
Celery tasks for the alerts engine.

- evaluate_all_alert_rules: runs on a 30s beat schedule, evaluates every
  active AlertRule across all tenants and fires notifications + WebSocket
  pushes when conditions are met.
"""
import logging
import operator

from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger('pipeline')

OPERATOR_MAP = {
    '>': operator.gt,
    '<': operator.lt,
    '==': operator.eq,
    '!=': operator.ne,
}


@shared_task
def evaluate_all_alert_rules():
    """Evaluate every active AlertRule and create Notifications where triggered."""
    from alerts.models import AlertRule, Notification
    from assets.models import Tank, PipelineSegment
    from operations.models import Batch, VesselDischarge

    channel_layer = get_channel_layer()
    rules = AlertRule.objects.filter(is_active=True).select_related('tenant')
    fired = 0

    for rule in rules:
        entities = _get_entities(rule)
        op_func = OPERATOR_MAP.get(rule.condition)
        if not op_func:
            continue

        for entity in entities:
            value = _get_metric_value(entity, rule.metric)
            if value is None:
                continue

            if op_func(value, rule.threshold):
                msg = rule.message_template.format(
                    entity=str(entity), value=value,
                )
                notification = Notification.objects.create(
                    tenant=rule.tenant,
                    rule=rule,
                    message=msg,
                )
                fired += 1

                # Push via WebSocket
                try:
                    async_to_sync(channel_layer.group_send)(
                        f'tenant_{rule.tenant_id}',
                        {
                            'type': 'alert_notification',
                            'data': {
                                'id': notification.id,
                                'message': msg,
                                'rule': rule.name,
                                'entity_type': rule.entity_type,
                                'created_at': str(notification.created_at),
                            },
                        }
                    )
                except Exception as e:
                    logger.warning(f'WebSocket push failed for notification {notification.id}: {e}')

    logger.info(f'Alert evaluation complete: {fired} notifications fired.')
    return fired


def _get_entities(rule):
    """Return QuerySet of entities matching the rule's entity_type and optional entity_id."""
    from assets.models import Tank, PipelineSegment
    from operations.models import Batch, VesselDischarge

    MODEL_MAP = {
        'TANK': Tank,
        'PIPELINE': PipelineSegment,
        'BATCH': Batch,
        'VESSEL': VesselDischarge,
    }
    model = MODEL_MAP.get(rule.entity_type)
    if not model:
        return []

    qs = model.objects.all()

    # Scope to tenant
    if rule.entity_type == 'TANK':
        qs = qs.filter(depot__tenant=rule.tenant)
    elif rule.entity_type == 'BATCH':
        qs = qs.filter(segment__tenant=rule.tenant)
    else:
        qs = qs.filter(tenant=rule.tenant)

    if rule.entity_id:
        qs = qs.filter(pk=rule.entity_id)

    return qs


def _get_metric_value(entity, metric):
    """Safely extract a metric value from an entity instance."""
    try:
        val = getattr(entity, metric, None)
        if callable(val):
            val = val()
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None
