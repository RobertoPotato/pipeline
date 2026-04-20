from django.urls import path, include
from rest_framework.routers import DefaultRouter
from alerts.views import (
    AlertRuleViewSet, NotificationViewSet,
    NotificationListView, AlertRuleListView, AlertRuleCreateView
)

router = DefaultRouter()
router.register(r'rules', AlertRuleViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('history/', NotificationListView.as_view(), name='notification_list'),
    path('rules/', AlertRuleListView.as_view(), name='alert_rules'),
    path('rules/add/', AlertRuleCreateView.as_view(), name='alert_rule_add'),
]
