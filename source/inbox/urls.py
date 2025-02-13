from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.InboxView.as_view(), name='inbox'),
    path('inbox/<int:message_id>/', views.InboxMessageDetailView.as_view(), name='inbox-message'),
]
