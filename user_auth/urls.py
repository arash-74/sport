from django.urls import path

from user_auth import views
app_name = 'user_auth'
urlpatterns = [
    path('register', views.register_view, name='register'),
    path('send-otp', views.send_otp_code, name='send otp'),
    path('profile', views.profile_view, name='profile'),
    path('session-is-valid', views.session_is_valid, name='session is valid'),
    path('logout', views.logout_view, name='logout'),
]