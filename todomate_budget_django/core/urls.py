from django.contrib import admin
from django.urls import path, include

from core.views import home_redirect, planner_dashboard
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('core.api_urls')),
    path('', home_redirect, name='home'),
    path('planner/', planner_dashboard, name='planner_dashboard'),
    path('tasks/', include('tasks.urls')),
    path('finance/', include('finance.urls')),
]
