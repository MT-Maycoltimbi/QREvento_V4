from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # identification = models.TextField(max_length=500, blank=True)
    roles = [
        ('admin', 'Administrador'),
        ('user', 'Usuario'),]
    role = models.CharField(max_length=10, choices=roles, default="user")
    ciudad = models.CharField(max_length=80, default=0)
    ocupacion = models.CharField(max_length=100, default=0)

    cedula = models.CharField(max_length=10, default=0)
    age = models.PositiveIntegerField(default=0)
    sexos = [
        ('F', 'Femenino'),
        ('M', 'Masculino'),
        ('O', 'Otro'),
    ]
    sexo = models.CharField(max_length=1, choices=sexos, default='F')
    opcionSiNo = [
        ('si', 'Si'),
        ('no', 'No'),
    ]
    discapacidad = models.CharField(
        max_length=3, choices=opcionSiNo, default='no')
    acompañante = models.CharField(
        max_length=3, choices=opcionSiNo, default='no')
    opcionEducacion = [
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
        ('tercer', 'Tercer Nivel'),
    ]
    educacion = models.CharField(
        max_length=20, choices=opcionEducacion, default='secundaria')
    address = models.CharField(max_length=80, default=0)
    phone = models.PositiveIntegerField(default=0)
    op = [
        ('medios', 'medios impresos'),
        ('amigo', 'amigos'),
        ('redes', 'redes sociales')
    ]
    info = models.CharField(max_length=30, choices=op, default='amigo')
    data = models.CharField(max_length=255)
    imagen = models.ImageField(
        upload_to='C:/Users/micha/Desktop/QREvento/Aplicaciones/qr/static/codigos_qr')


class Eventos(models.Model):
    id_evento = models.AutoField(primary_key=True)
    name_evento = models.CharField(max_length=50, default=0)
    ubicacion = models.CharField(max_length=80, default=0)
    tipo_evento = models.CharField(max_length=50, default=0)
    responsable = models.CharField(max_length=30, default=0)
    requisitos = models.CharField(max_length=100, default=0)
    contacto = models.PositiveIntegerField(default=0)
    fecha_evento = models.CharField(max_length=20)
    hora_evento = models.CharField(max_length=20)
    cupos = models.PositiveIntegerField(default=10)
    descripcion = models.CharField(max_length=300, default=0)
    enlace = models.CharField(max_length=100)
    mi_lista = ArrayField(models.CharField(max_length=900), default=list)
    ingresos = ArrayField(models.CharField(max_length=900), default=list)
    estado= models.CharField(max_length=50, default='activo')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
