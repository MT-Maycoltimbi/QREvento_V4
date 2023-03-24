from django.urls import path, re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import (handler400, handler403, handler404, handler500)
from django.http import HttpResponseNotFound

handler404 = 'Aplicaciones.qr.views.error_404_view'
app_name = 'gestion'
urlpatterns = [
    path('', views.home, name='home'),
    path("crear_evento/", views.crear_evento, name="crear_evento"),
    path("autent_qr/", views.autent_qr, name="autent_qr"),
    path("verificar_Invitados/<id_evento>", views.verificar, name="verificar"),
    path("Inscripciones/", views.Inscripciones, name="Inscripciones"),
    path("event_creado/", views.event_creado, name="event_creado"),
    path("editar_evento/<id_evento>", views.editar_evento, name="editar_evento"),
    path("elimitar_evento/<id_evento>", views.eliminar_evento, name="eliminar_evento"),
    path("charts/", views.charts, name="charts"),
    path("descarga/<id_evento>", views.pdf, name="pdf"),
    # Modulo de autenticacion
    path('signup/', views.signup, name='signup'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    path('recover/', views.recover, name='recover'),
    # Modulo de administracion
    path('administrador/dashboard/', views.dashboard, name='dashboard'),
    #path('administrador/registrar/', views.registrar, name="registrar"),
    # path('administrador/editar/', views.editar),
    # path('administrador/edicion/<id>', views.edicion, name="edicion"),
    path('administrador/eliminar/<id>', views.eliminar, name="eliminar"),
    # Modulo de usuarios
    path('user/<id>/<nombre>', views.datos, name="datos"),
    path('registro_usuario/<nombre>', views.registro_usuario, name="registro_usuario"),
    #path('qr-scanner/', views.qr_scanner, name='qr_scanner'),
    path('registro_usuario/confirmacion_datos', views.confirmar_datos, name="confirmar_datos"),
    re_path(r'^.*/$', views.mi_vista, name="mi_vista"),
    
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)