from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('switch-language/<str:lang>/', views.switch_language, name='switch_language'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.complete_profile, name='complete_profile'),
    path('doctors/', views.doctors_list, name='doctors_list'),
    path('appointments/', views.appointments_page, name='appointments'),
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/<int:appointment_id>/approve/', views.approve_appointment, name='approve_appointment'),
    path('appointments/<int:appointment_id>/reject/', views.reject_appointment, name='reject_appointment'),
    path('appointments/<int:appointment_id>/no-show/', views.no_show_appointment, name='no_show_appointment'),
    path('appointments/<int:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),
    path('medical-records/', views.medical_records_page, name='medical_records'),
    path('lab-results/', views.lab_results_page, name='lab_results'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('api/doctor-slots/', views.doctor_slots_api, name='doctor_slots_api'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path("chatbot/", views.chatbot_reply, name="chatbot"),
    path('my-analysis-files/', views.my_analysis_files, name='my_analysis_files'),
    path('register/', views.register, name='register'),
    path('reports/', views.reports, name='reports'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
