from django.contrib import admin # type: ignore
from django.urls import path # type: ignore
from paginas import views

urlpatterns = [
    path('', views.home, name='home'),
    path("contacto/", views.contact, name="contact"),

    # NOTARIA
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
   
    path('horario-atencion/', views.horario_atencion, name='horario_atencion'),
    path('tramites-mas-comunes/', views.tramites_comunes, name='tramites_comunes'),
    path('preguntas-frecuentes/', views.preguntas_frecuentes, name='preguntas_frecuentes'),
    path('enlaces-interes/', views.enlaces_interes, name='enlaces_interes'),

    # SERVICIOS NOTARIALES
    path('servicios-notariales/', views.servicios_notariales, name='servicios_notariales'),
    path('escrituras-publicas/', views.escrituras_publicas, name='escrituras_publicas'),
    path('solicitud-escrituras/', views.solicitud_escrituras, name='solicitud_escrituras'),
    path('validar-documentos/', views.validar_documentos, name='validar_documentos'),
    path('seguimiento-escrituras/', views.seguimiento_escrituras, name='seguimiento_escrituras'),
    path('notaria-en-linea/', views.notaria_en_linea, name='notaria_en_linea'),
    path("tramites/", views.tramites_list, name="tramites_list"),
    path("tramites/<int:tramite_id>/", views.tramite_detail, name="tramite_detail"),
    path('documentos-privados/', views.documentos_privados, name='documentos_privados'),
    path('admin/', admin.site.urls),
]