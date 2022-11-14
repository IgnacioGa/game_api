from django.urls import path
from user.views import CustomTokenRefreshView, MyTokenObtainPairView, UserCreate, UsersList, index

urlpatterns = [
    path('', MyTokenObtainPairView.as_view()),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    path('user-list/', UsersList.as_view()),
    path('create/', UserCreate.as_view()),
    path('test', index, name="index"),
]
