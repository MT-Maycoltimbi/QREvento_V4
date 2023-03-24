from django.shortcuts import render, redirect, reverse, get_object_or_404
from .models import Profile, Eventos
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
import matplotlib.pyplot as plt
from io import BytesIO
import qrcode
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
import os
# from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from pyzbar.pyzbar import decode
import cv2
import pyzbar.pyzbar as pyzbar
from datetime import datetime
from datetime import date


# Create your views here.


def isAdmin(request):
    return request.user.profile.role == "admin"


def home(request):
    return render(request, "home.html")


@login_required
def Inscripciones(request):
    if isAdmin(request):
        return render(request, 'inscripciones.html')
    else:
        return render(request, 'error_404.html')


@login_required
def crear_evento(request):
    if isAdmin(request):
        if request.method == "GET":
            return render(request, "crear-event.html")

        else:
            evento_name = request.POST['evento_name']
            ubicacion = request.POST['ubicacion']
            tipo_evento = request.POST['tipo_evento']
            responsable = request.POST['responsable']
            requisitos = request.POST['requisitos']
            contacto = request.POST['contacto']
            fecha_evento = request.POST['fecha_evento']
            hora_evento = request.POST['hora_evento']
            cupos = request.POST['cupos']
            descripcion = request.POST['descripcion']
            evento = Eventos()
            evento.name_evento = evento_name
            evento.ubicacion = ubicacion
            evento.tipo_evento = tipo_evento
            evento.responsable = responsable
            evento.requisitos = requisitos
            evento.contacto = contacto
            evento.fecha_evento = fecha_evento
            evento.hora_evento = hora_evento
            evento.cupos = cupos
            evento.descripcion = descripcion
            evento.save()
            return render(request, "crear-event.html", {"evento": evento, 'mensaje': "evento creado con exito"})


def editar_evento(request, id_evento):

    letras = 0
    for i in str(id_evento):
        if i not in "1234567890":
            letras += 1
    condicion = letras == 0

    if not (isAdmin(request)) or not (condicion):
        return render(request, 'error_404.html')

    else:

        if request.method == "GET":
            eventos = Eventos.objects.get(id_evento=id_evento)
            return render(request, 'editar_evento.html', {"evento": eventos})
        else:
            evento_name = request.POST['evento_name']
            ubicacion = request.POST['ubicacion']
            tipo_evento = request.POST['tipo_evento']
            responsable = request.POST['responsable']
            requisitos = request.POST['requisitos']
            contacto = request.POST['contacto']
            fecha_evento = request.POST['fecha_evento']
            hora_evento = request.POST['hora_evento']
            cupos = request.POST['cupos']
            descripcion = request.POST['descripcion']
            id = request.POST["id_evento"]
            evento = Eventos.objects.get(id_evento=id)
            evento.name_evento = evento_name
            evento.ubicacion = ubicacion
            evento.tipo_evento = tipo_evento
            evento.responsable = responsable
            evento.requisitos = requisitos
            evento.contacto = contacto
            evento.fecha_evento = fecha_evento.strftime('%d/%m/%Y')
            evento.hora_evento = hora_evento
            evento.cupos = cupos
            evento.descripcion = descripcion
            evento.save()
            return redirect('gestion:event_creado')


@login_required
def event_creado(request):
    if isAdmin(request):
        if request.method == "GET":
            evento = Eventos.objects.all()

            return render(request, "event_creado.html", {"evento": evento})

    else:
        return render(request, 'error_404.html')


def eliminar_evento(request, id_evento):
    evento = Eventos.objects.get(id_evento=id_evento)
    evento.delete()
    return redirect('gestion:event_creado')


def registro_usuario(request, nombre):
    if request.method == "GET":
        return render(request, 'registro_usuario.html')
    else:
        try:

            cedula = request.POST['txtcedula']
            print(cedula)
            name = request.POST.get('txtname', '')
            apellido = request.POST['txtlname']
            email = request.POST['txtemail']
            ciudad = request.POST['txtciudad']
            address = request.POST['txtad']
            ocupacion = request.POST['txtocupacion']
            sexo = request.POST['txtsex']
            discapacidad = request.POST['txtdiscapacidad']
            acompañante = request.POST['txtacompañante']
            educacion = request.POST['txteducacion']
            age = request.POST['txtage']
            phone = request.POST['txtphone']
            info = request.POST['txtinfo']

            prueba = User.objects.all()
            t, identificador = '', 0
            for usu in prueba:
                if usu.username == name+apellido+str(phone):
                    t += 'ya existe'
                    identificador = usu.id
            c = t == 'ya existe'

            rutaCompleta = 'C:/Users/micha/Desktop/QREvento/Aplicaciones/qr/static/codigos_qr/'
            evento = Eventos.objects.get(name_evento=nombre)

            if len(evento.mi_lista) < evento.cupos:
                if c:

                    usuario = User.objects.get(id=identificador)
                    mi_lista = evento.mi_lista
                    print(mi_lista)
                    if str(identificador) in mi_lista:
                        mensaje = "El usuario ya está inscrito en este evento."
                        return render(request, "registro_usuario.html", {'mensaje': mensaje})
                    mi_lista.append(identificador)
                    evento.save()

                    ruta = ''
                    r = str(usuario.profile.imagen).split("/")
                    print(usuario.profile.imagen)
                    cont = 0

                    for i in r:
                        if i != "static":
                            cont += 1
                        else:
                            break
                    r = r[cont:]
                    for i in r:
                        ruta += "/"+i

                    asunto = "invitacion - "+name.upper()
                    mensaje = "Bienevnido/a! " + name.upper() + " gracias por regristrate al evento: "+nombre+", realizado por el GAD Crnel. Marcelino Maridueña nos complace que hayas podido registrarte con exito. Esperamos que disfrutes de todas las actividades y experiencias que hemos preparados para ti.\n \nPara ingresar al evento debes presentar este codigo QR el dia del evento\n Fecha - hora: " + \
                        evento.fecha_evento+" - " + evento.hora_evento + \
                        "\n Direccion: "+evento.ubicacion + "\n Responble del evento:" + evento.responsable + \
                        "\n Que tengas un excelente dia. Te esperamos"
                    email_desde = settings.EMAIL_HOST_USER
                    email_para = [email]
                    correo = EmailMessage(
                        asunto,
                        mensaje,
                        email_desde,
                        email_para,)
                    ruta1 = rutaCompleta+str(r[-1])
                    with open(ruta1, 'rb') as qr_file:
                        print("entró")
                        correo.attach(usuario.first_name+'.png',
                                      qr_file.read(), 'image/png')
                    correo.send(fail_silently=False)
                    print("entró")
                    evento = {}
                    evento["evento"] = nombre
                    return render(request, "usuario.html", {'usuario': usuario, 'evento': evento, 'ruta': ruta})

                else:
                    print("no existe")
                    usuario = User.objects.create_user(
                        username=name+apellido+str(phone), first_name=name, last_name=apellido, email=email)
                    usuario.profile.address = address
                    usuario.profile.cedula = cedula
                    usuario.profile.ciudad = ciudad
                    usuario.profile.ocupacion = ocupacion
                    usuario.profile.sexo = sexo
                    usuario.profile.discapacidad = discapacidad
                    usuario.profile.acompañante = acompañante
                    usuario.profile.educacion = educacion
                    usuario.profile.age = age
                    usuario.profile.phone = phone
                    usuario.profile.info = info
                    usuario.profile.data = str(usuario.id)
                    usuario.save()

                    usuario = User.objects.get(
                        username=name+apellido+str(phone))

                    # Crear el código QR a partir de la información del usuario
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(usuario.profile.data)
                    qr.make(fit=True)

                    img = qr.make_image(fill_color="black", back_color="white")

                    # Guardar el código QR como una imagen en la base de datos
                    qr_image = InMemoryUploadedFile(
                        BytesIO(), 'ImageField', 'qr.png', 'image/png', img.size, None)
                    qr_image.file = BytesIO()
                    img.save(qr_image.file, 'PNG')
                    qr_image.file.seek(0)

                    # Actualizar el atributo imagen en el objeto Profile
                    usuario.profile.imagen.save(
                        f'{usuario.profile.data}.png', qr_image, save=True)
                    print(usuario.profile.imagen)
                    ruta = ''
                    r = str(usuario.profile.imagen).split("/")
                    print(r)
                    cont = 0
                    for i in r:
                        if i != "static":
                            cont += 1
                        else:
                            break
                    r = r[cont:]
                    for i in r:
                        ruta += "/"+i
                    print(ruta)
                    evento = Eventos.objects.get(name_evento=nombre)
                    mi_lista = evento.mi_lista
                    mi_lista.append(usuario.id)
                    evento.save()

                    # Envía el correo
                    asunto = "invitacion -"+str(name)
                    mensaje = "Bienevnido/a! " + name.upper() + " gracias por regristrate al evento: "+nombre+", realizado por el GAD Crnel. Marcelino Maridueña nos complace que hayas podido registrarte con exito. Esperamos que disfrutes de todas las actividades y experiencias que hemos preparados para ti.\n \nPara ingresar al evento debes presentar este codigo QR el dia del evento\n Fecha - hora: " + \
                        evento.fecha_evento+" - " + evento.hora_evento + \
                        "\n Direccion: "+evento.ubicacion + "\n Responble del evento:" + evento.responsable + \
                        "\n Que tengas un excelente dia. Te esperamos"
                    email_desde = settings.EMAIL_HOST_USER
                    email_para = [email]
                    correo = EmailMessage(
                        asunto,
                        mensaje,
                        email_desde,
                        email_para,)
                    ruta1 = rutaCompleta+str(r[-1])
                    with open(ruta1, 'rb') as qr_file:
                        print("entró")
                        correo.attach(usuario.first_name+'.png',
                                      qr_file.read(), 'image/png')

                    correo.send(fail_silently=False)
                    print("entró")

                    evento = {}
                    evento["evento"] = nombre
                    # print(img_bytes.getvalue())
                    # return HttpResponse(img_bytes.getvalue(), content_type="image/png")
                    return render(request, "usuario.html", {'usuario': usuario, 'evento': evento, 'ruta': ruta})
            else:
                return render(request, 'agotado.html')
        except:

            return render(request, "error_404.html")


def confirmar_datos(request):
    if request.method == "GET":
        usuarios = User.objects.all().select_related('profile')
        return render(request, 'confirmar_datos.html', {"usuario": usuarios})
    else:

        return render(request, "usuario.html")


def datos(request, id, nombre):
    try:
        usuario = User.objects.get(id=id)
        condicion = str(id) == str(usuario.id) and str(
            usuario.first_name) == str(nombre)
        if condicion:
            return render(request, "usuario.html", {"usuario": usuario})
        else:
            return render(request, "error_404.html")
    except:
        return render(request, "error_404.html")


@login_required
def autent_qr(request):
    if isAdmin(request):
        if request.method == "GET":
            evento = Eventos.objects.all()

            return render(request, "autent_qr.html", {"evento": evento})

    else:
        return render(request, 'error_404.html')


def verificar(request, id_evento):
    evento = Eventos.objects.get(id_evento=id_evento)

    cap = cv2.VideoCapture(0)  # Accede a la cámara del dispositivo
    while True:
        _, frame = cap.read()  # Lee el marco de la cámara

        # Decodifica el código QR
        decoded_objects = pyzbar.decode(frame)

        if decoded_objects:  # Verifica si se detectó algún código QR
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')

                if data in evento.mi_lista:
                    if data in evento.ingresos:
                        dic = {}
                        dic['ingreso'], dic['nombre'] = 'El QR ya ha sido verificado y usado', evento.name_evento
                        cv2.destroyAllWindows()  # Cierra la ventana de OpenCV antes de mostrar el resultado
                        return render(request, 'resultado_qr.html', {'data': data, 'dic': dic})
                    else:
                        evento.ingresos += [data]
                        evento.save()

                        dic = {}
                        dic['ingreso'], dic['nombre'] = 'SI tiene acceso', evento.name_evento

                    try:
                        usuario = User.objects.get(id=int(data))
                        cv2.destroyAllWindows()  # Cierra la ventana de OpenCV antes de mostrar el resultado
                        return render(request, 'resultado_qr.html', {'data': data, 'dic': dic, 'usuario': usuario})
                    except User.DoesNotExist:
                        error = "Usuario no existe o fue eliminado"
                        cv2.destroyAllWindows()  # Cierra la ventana de OpenCV antes de mostrar el resultado
                        return render(request, "autent_qr.html", {"evento": evento, "error": error})

            # Si se procesaron todos los códigos QR y ninguno fue autorizado
            dic = {'ingreso': 'No tiene acceso', 'nombre': evento.name_evento}
            cv2.destroyAllWindows()  # Cierra la ventana de OpenCV antes de mostrar el resultado
            return render(request, 'resultado_qr.html', {'data': data, 'dic': dic})

        # Muestra el marco de la cámara en la pantalla
        cv2.imshow("QR Scanner", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break

    # Libera los recursos de la cámara y cierra la ventana
    cap.release()
    cv2.destroyAllWindows()
    return render(request, 'pagina.html')


@login_required
def dashboard(request):
    if isAdmin(request):
        return render(request, "index.html")
    else:
        return render(request, 'error_404.html')


def asistencia_eventos():
    evento = []
    asis = []
    indices_may = []
    indices_men = []
    even_may = []
    even_men = []
    eventos = Eventos.objects.all()

    for i in eventos:
        nombre = i.name_evento
        persona = i.mi_lista
        if nombre not in evento:
            evento.append(nombre)
            numero_de_asistencias = len(persona)
            asis.append(numero_de_asistencias)
        else:
            print("solo eventos")

    for indice, elemento in enumerate(asis):
        if elemento == max(asis):
            indices_may.append(indice)
        elif elemento == min(asis):
            indices_men.append(indice)
        else:
            print("solo indices")

    for j in indices_may:
        print(evento[j])
        even_may.append(evento[j])

    for h in indices_men:
        print(evento[h])
        even_men.append(evento[h])

    return (even_may, even_men)


def charts_estadistico():
    sexo = []
    direccion = []
    edad = []
    asistencia = []
    eventos = Eventos.objects.all()
    for fila in eventos:
        usuario_id = fila.mi_lista
        for j in usuario_id:
            perfil = User.objects.get(id=int(j))
            direccion.append(perfil.profile.address)
            edad.append(perfil.profile.age)
            if perfil.profile.sexo == 'M':  # CANTIDAD DE HOMBRES Y MUJERES
                sexo.append('Hombre')
            elif perfil.profile.sexo == 'F':
                sexo.append('Mujer')
            else:
                sexo.append('Otros')
    for j in eventos:
        nombre = j.name_evento
        persona = j.mi_lista
        if nombre not in eventos:
            numero_de_asistencias = len(persona)
            asistencia.append(numero_de_asistencias)
        else:
            print("solo eventos")

    return (sexo, direccion, edad, asistencia)


@login_required
def charts(request):
    if isAdmin(request):
        eventos = Eventos.objects.all()
        # evento1=Eventos.objects.get(id_evento=1)
        # print(evento1.mi_lista)
        ocupacion = [' Médico/a', ' Enfermero/a', ' Ingeniero/a', ' Abogado/a', ' Maestro/a', ' Arquitecto/a', ' Chef/Cocinero/a', ' Carpintero/a', ' Electricista', ' Plomero/a', ' Mecánico/a', ' Diseñador/a gráfico/a', ' Periodista', ' Escritor/a', ' Fotógrafo/a', ' Artista plástico/a', ' Actor/actriz', ' Bailarín/bailarina',
                     ' Deportista/profesional del deporte', ' Político/a', ' Empresario/a', ' Analista financiero/a', ' Investigador/a', ' Psicólogo/a', ' Trabajador/a social', ' Administrador/a de empresas', ' Agente de seguros', ' Vendedor/a', ' Servidor/a de atención al cliente', ' Operador/a de maquinaria pesada', ' Otro/a']
        dato_o = [0]*30
        num_mes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        hombres = [0]*12
        mujeres = [0]*12
        otros = [0]*12
        sexo = []
        direccion = []
        edad = []
        asistencia = []
        no_acompa, acompa, disca, no_disca, rede, amigo, medios, primaria, secundaria, superior = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        for fila in eventos:
            usuario_id = fila.mi_lista
            for j in usuario_id:
                perfil = User.objects.get(id=int(j))
                fecha = fila.fecha_evento.split('/')
                posicion = num_mes.index(int(fecha[1]))
                direccion.append(perfil.profile.address)
                edad.append(perfil.profile.age)

                if perfil.profile.sexo == 'M':  # CANTIDAD DE HOMBRES Y MUJERES
                    hombres[posicion] += 1
                    sexo.append('Hombre')
                elif perfil.profile.sexo == 'F':
                    mujeres[posicion] += 1
                    sexo.append('Mujer')
                else:
                    otros[posicion] += 1
                    sexo.append('Otros')
                if perfil.profile.acompañante == 'si':  # PORCENTAJE ACOMPAÑANTE
                    acompa += 1
                else:
                    no_acompa += 1
                if perfil.profile.discapacidad == 'si':  # PORCENTAJE DISCAPACITADOS
                    disca += 1
                else:
                    no_disca += 1
                if perfil.profile.ocupacion in ocupacion:  # Porcentaje por ocupacion
                    indice = ocupacion.index(perfil.profile.ocupacion)
                    dato_o[indice] += 1

                if perfil.profile.educacion == 'primaria':  # Porcentaje por nivel educativo
                    primaria += 1
                elif perfil.profile.educacion == 'secundaria':
                    secundaria += 1
                else:
                    superior += 1
                if perfil.profile.info == 'redes':  # Como se enteraron del evento
                    rede += 1
                elif perfil.profile.info == 'medios':
                    medios += 1
                else:
                    amigo += 1
        # para la direccion
        dir_count = {}
        for d in direccion:
            if d in dir_count:
                dir_count[d] += 1
            else:
                dir_count[d] = 1
        top3_mayor = dict(
            sorted(dir_count.items(), key=lambda x: x[1], reverse=True)[:2])
        top3_menor = dict(sorted(dir_count.items(), key=lambda x: x[1])[:2])

        x = asistencia_eventos()
        asis_may = x[0]
        asis_men = x[1]

        c = charts_estadistico()
        asistencia = c[3]
        edad = c[2]

        # Para asistencia
        if len(asistencia) > 5:
            exceso = []
            for i in asistencia[5:]:
                exceso.append(i)
            prom = sum(exceso)/len(exceso)
            asistencia.insert(0, (asistencia[0]+prom)/2)
            asistencia.insert(4, (asistencia[4]+prom)/2)
            asistencia = asistencia[:5]
        else:
            promedio = sum(asistencia)/len(asistencia)
            cantidad = 5-len(asistencia)
            for i in range(cantidad):
                asistencia.append(promedio)
        # Para edad
        if len(edad) > 5:
            exce = edad[5:]
            prom = sum(exce)/len(exce)
            edad.insert(0, (edad[0]+prom)/2)
            edad.insert(4, (edad[4]+prom)/2)
            edad = edad[:5]
        else:
            promedio_1 = sum(edad)/len(edad)
            cantidad_1 = 5-len(edad)
            for i in range(cantidad_1):
                edad.append(promedio_1)

        print(asistencia)
        print(edad)
        return render(request, 'charts.html', {'hombres': hombres, 'mujeres': mujeres, 'otros': otros, 'no_acompa': no_acompa, 'acompa': acompa, 'no_disca': no_disca, 'disca': disca, 'rede': rede, 'amigo': amigo, 'medios': medios, 'primaria': primaria, 'secundaria': secundaria, 'superior': superior, 'dato_o': dato_o, 'asis_may': asis_may, 'asis_men': asis_men, 'asistencia': asistencia, 'sexo': sexo, 'direccion': direccion, 'edad': edad, 'top3_mayor': top3_mayor, 'top3_menor': top3_menor})
    else:
        return render(request, 'error_404.html')


def pdf(request, id_evento):
    if request.method == "GET":
        usuarios = User.objects.all().select_related('profile')
        evento = Eventos.objects.get(id_evento=id_evento)
        l = []
        for elemento in evento.mi_lista:
            l.append(int(elemento))
        evento.mi_lista = l
        evento.save()

        print(evento.mi_lista)

        return render(request, "charts2.html", {"usuario": usuarios, 'evento': evento})


@login_required
def Inscripciones(request):
    if request.method == "GET":
        usuarios = User.objects.all().select_related('profile')
        evento = Eventos.objects.all()
        print('hola')

        for fila in evento:
            lista = []
            l = fila.mi_lista
            for valor in l:
                lista.append(int(valor))
            fila.mi_lista = lista
            fila.save()
            print('hola2')
            print(fila.mi_lista)

        return render(request, "inscripciones.html", {"usuario": usuarios, 'evento': evento})


@login_required
def eliminar(request, id):
    usuario = User.objects.get(id=id)
    usuario.delete()
    return redirect('gestion:Inscripciones')


def signup(request):
    if request.method == 'GET':
        return render(request, 'register.html', {'form': UserCreationForm})
    else:

        usuarios = User.objects.all().select_related('profile')
        valor = 0
        for i in usuarios:
            if i.profile.role == "admin":
                valor += 1
        if (request.POST['password1'] == request.POST['password2']) and valor < 2:
            try:
                usuario = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'],
                    email=request.POST['email'])
                usuario.profile.role = "admin"

                asunto = "Registro Exitoso"
                mensaje = "Bienvenido/a! a  QREvento nos complace tenerte como parte de nuestra comunidad de administrador \nUsername: " + \
                    request.POST['username']+"\ncontraseña: " + \
                    request.POST['password1']+"\n"
                email_desde = settings.EMAIL_HOST_USER
                email_para = [request.POST['email']]
                correo = EmailMessage(
                    asunto,
                    mensaje,
                    email_desde,
                    email_para,)
                correo.send(fail_silently=False)

                usuario.save()
                login(request, usuario)

                if (usuario.profile.role == "admin"):
                    return redirect('gestion:dashboard')
                else:
                    url = reverse("gestion:datos", args=[usuario.id])
                    return redirect(url)
            except IntegrityError:
                return render(request, 'register.html', {
                    'form': UserCreationForm,
                    'error': 'usuario ya existe'})
        return render(request, 'register.html', {
            'form': UserCreationForm,
            'error': 'contraseñas no coinciden o ya están registrados un maximo de dos administradores'})


def signout(request):
    logout(request)
    return redirect('gestion:signin')


def signin(request):
    if request.method == 'GET':
        return render(request, 'login.html', )
    else:
        usuario = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])

        if usuario is None:
            return render(request, 'login.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o contraseña inexistentes o invalidos'})
        else:
            login(request, usuario)
            if (usuario.profile.role == "admin"):
                return redirect('gestion:dashboard')
            else:
                url = reverse("gestion:datos", args=[usuario.id])
                return redirect(url)


def recover(request):
    if request.method == 'GET':
        return render(request, 'recover.html')
    else:

        correo = request.POST.get('txtemail', '')
        contraseña = request.POST['password']
        print(correo)
        if (correo != ""):
            usuarios = User.objects.all().select_related('profile')
            for usu in usuarios:
                if (usu.email == correo) and (usu.profile.role == "admin"):
                    print(usu.username)
                    usu.set_password(contraseña)
                    usu.save()
                    mensaje = "hola "+usu.username+"\n \ntu contraseña es: "+contraseña
                    email_desde = settings.EMAIL_HOST_USER
                    email_para = [correo]
                    envio = EmailMessage(
                        "Contraseña Extraviada",
                        mensaje,
                        email_desde,
                        email_para,)

                    envio.send(fail_silently=False)
        return redirect('gestion:signin')


def error_404_view(request, exception):
    return render(request, 'error_404.html')


def mi_vista(request):
    return render(request, "error_404.html")
