# -*- coding: utf-8 -*-
import os

import datetime
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from AresLabControl.settings import BASE_DIR, EMAIL_HOST_USER
from LabModule.app_forms.Maquina import MaquinaForm
from LabModule.app_forms.Mueble import MuebleForm
from LabModule.app_forms.Mueble import PosicionesMuebleForm
from LabModule.app_forms.Solicitud import SolicitudForm
from LabModule.app_models.Maquina import Maquina
from LabModule.app_models.Mueble import Mueble
from LabModule.app_models.MuebleEnLab import MuebleEnLab
from LabModule.app_models.Paso import Paso
from LabModule.app_models.Proyecto import Proyecto
from LabModule.app_models.Solicitud import Solicitud
from LabModule.app_models.SolicitudMaquina import SolicitudMaquina
from LabModule.app_models.Usuario import Usuario
from LabModule.app_utils.notificaciones import enviar_correo


def maquina_add(request, template_name = 'maquinas/agregar.html'):
    """Comporbar si el usuario puede agregar una máquina y obtener los campos necesarios.
        Historia de usuario: `ALF-18 <http://miso4101-2.virtual.uniandes.edu.co:8080/browse/ALF-18 />`_ :
        Yo como Jefe de Laboratorio quiero poder agregar nuevas máquinas en el sistema para que puedan ser usadas por los asistentes.
        Se encarga de:
            * Comprobar si hay un usario logeuado
            * Comprobar si el suario tiene permisos para agregar máquinas
            * Obtener los campos y archivos para redireccionarlos a :func:`comprobarPostMaquina` así
              como decirle el section
            * Definir el template a usar
     :param request: El HttpRequest que se va a responder.
     :type request: HttpRequest.
     :param template_name: La template sobre la cual se va a renderizar.
     :type template_name: html.
     :param section: Objeto que permite diferenciar entre la modificación de una máquina y la adición de esta.
     :type section: {‘title’:,’agregar’}.
     :returns: HttpResponse -- La respuesta a la petición, en caso de que todo salga bien redirecciona a
     la modificación de la nueva
                               máquina. Sino redirecciona al mismo formulario mostrando los errores.
                               Si no esta autorizado se envia un código 401
    """
    if request.user.is_authenticated() and request.user.has_perm("LabModule.can_addMachine"):
        section = {'title': 'Agregar Máquina', 'agregar': True}
        mensaje = ""

        form = MuebleForm(request.POST or None, request.FILES or None)
        formMaquina = MaquinaForm(request.POST or None, request.FILES or None)
        formPos = PosicionesMuebleForm(request.POST or None, request.FILES or None)

        if request.method == 'POST':
            return comprobarPostMaquina(form, formMaquina, formPos, request, template_name, section)
        context = {'form'       : form,
                   'formMaquina': formMaquina,
                   'formPos'    : formPos,
                   'mensaje'    : mensaje,
                   'section'    : section,
                   'start': request.GET.get('start', ''),
                   'end': request.GET.get('end', '')
                   }
        return render(request, template_name, context)
    else:
        return HttpResponse('No autorizado', status = 401)


def maquina_detail(request, pk, template_name = 'maquinas/detalle.html'):
    if request.user.is_authenticated() and request.user.has_perm("LabModule.can_viewMachine"):
        section = {'title': 'Ver Detalle ', 'agregar': "ver"}

        maquina = get_object_or_404(Maquina, pk = pk)
        mueble = maquina.mueble
        laboratorio = MuebleEnLab.get_laboratorio(mueble)

        pos = MuebleEnLab.objects.get(idLaboratorio = laboratorio,
                                      idMueble = mueble)

        mensajeCalendario = "Este es el horario disponible de la máquina. Seleccione el horario que más le convenga"

        context = {'maquina'          : maquina,
                   'laboratorio'      : laboratorio,
                   'mueble'           : mueble,
                   'pos'              : pos,
                   'section'          : section,
                   'mensajeCalendario': mensajeCalendario}
        return render(request, template_name, context)
    else:
        return HttpResponse('No autorizado', status = 401)


def maquina_update(request, pk, template_name = 'maquinas/agregar.html'):
    """Comporbar si el usuario puede modificar una máquina, obtener los campos necesarios.
        Se encarga de:
            * Comprobar si hay un usario logeuado
            * Comprobar si el suario tiene permisos para modificar máquinas
            * Obtener los campos y archivos para redireccionarlos a :func:`comprobarPostMaquina` así
              como decirle el section
            * Definir el template a usar
     :param request: El HttpRequest que se va a responder.
     :type request: HttpRequest.
     :param template_name: La template sobre la cual se va a renderizar.
     :type template_name: html.
     :param pk: La llave primaria de la máquina a modificar
     :type pk: String.
     :param section: Objeto que permite diferenciar entre la modificación de una máquina y la adición de esta.
     :type section: {‘title’:,’agregar’}.
     :returns: HttpResponse -- La respuesta a la petición, en caso de que todo salga bien redirecciona a si mismo.
     Sino redirecciona al mismo formulario mostrando los errores. Si no esta autorizado se envia un código 401
    """

    if request.user.is_authenticated() and request.user.has_perm("LabModule.can_editMachine"):
        section = {'title': 'Modificar Máquina', 'agregar': False}

        inst_maquina = get_object_or_404(Maquina, pk = pk)
        inst_mueble = inst_maquina.mueble
        inst_ubicacion = get_object_or_404(MuebleEnLab, idMueble = inst_mueble)
        inst_maquina.fechaInicialDisp=inst_maquina.fechaInicialDisp.strftime("%Y-%m-%d %H:%M")
        inst_maquina.fechaFinalDisp = inst_maquina.fechaFinalDisp.strftime("%Y-%m-%d %H:%M")
        form = MuebleForm(request.POST or None,
                          request.FILES or None,
                          instance = inst_mueble)
        formMaquina = MaquinaForm(request.POST or None,
                                  request.FILES or None,
                                  instance = inst_maquina)
        formPos = PosicionesMuebleForm(request.POST or None,
                                       request.FILES or None,
                                       instance = inst_ubicacion)

        return comprobarPostMaquina(form, formMaquina, formPos, request, template_name, section)
    else:
        return HttpResponse('No autorizado', status = 401)


def maquina_list(request, template_name = 'maquinas/listar.html'):
    """Comprobar si el usario puede ver las máquinas y mostraselas filtrando por una búsqueda.
           Historia de usuario: ALF-20:Yo como Jefe de Laboratorio quiero poder filtrar las máquinas existentes por
           nombre para visualizar sólo las que me interesan.
           Historia de usuario: ALF-25:Yo como Asistente de Laboratorio quiero poder filtrar las máquinas existentes
           por nombre para visualizar sólo las que me interesan.
           Se encarga de:
               * Comprobar si hay un usario logueado
               * Comprobar si el suario tiene permisos para ver las máquinas
               * Obtener todas las máquinas cuyo nombre contenga el párametro solicitado por el usario
               * Páginar el resultado de la consulta.

        :param pag: Opcional: El número de página que se va a mostrar en la páginación.
        :type pag: Integer.
        :param que: Opcional: La búsqueda que se va a realizar
        :type que: String.
        :param num: Opcional: El número de máquinas a ver en cada página
        :type num: String.
        :returns: HttpResponse -- La respuesta a la petición. Retorna páginada la lista de las máquias que cumplen
         con la búsqueda. Si no esta autorizado se envia un código 401
    """
    if request.user.is_authenticated() and request.user.has_perm("LabModule.can_listMachine"):
        section = {'title': 'Listar Máquinas'}
        can_editMachine = request.user.has_perm("LabModule.can_editMachine")
        if not can_editMachine:
            lista_maquinas = Mueble.objects.all().filter(estado = True, tipo = 'maquina').order_by('id')
        else:
            lista_maquinas = Mueble.objects.all().filter(tipo = 'maquina').order_by('id')

        id_maquina = [maquina.id for maquina in lista_maquinas]
        lista__posiciones = MuebleEnLab.objects.all().filter(idMueble__in = id_maquina).order_by('idMueble_id')
        maquinas = Maquina.objects.all().filter(mueble_id__in = id_maquina).order_by('mueble_id')

        maquinasConUbicacion = zip(lista_maquinas, lista__posiciones, maquinas)

        context = {'section'       : section,
                   'lista_maquinas': maquinasConUbicacion}
        return render(request, template_name, context)
    else:
        return HttpResponse('No autorizado', status = 401)


def notificacion_solicitud_maquina(request, maquina_nombre, solicitud_id):
    """Realiza la notificación de solicitud de máquinas para el usuario que la necesita
               Historia de usuario: ALF-33:Yo como Jefe de Laboratorio quiero ser notificado vía correo electrónico
                    si se hizo una solicitud para poderla gestionar cuanto antes.
               Se encarga de:
                   * Realiza la notificación de la solicitud de máquinas
            :param request: El HttpRequest que se va a responder.
            :type request: HttpRequest.
            :param maquina_nombre: Máquina a solicitar
            :type maquina: Máquina.
            :param solicitud_id: Id de la solicitud de la máquina.
            :type id: Identificador.
       """
    jefes_lab = User.objects.filter(groups__name = 'Jefe de Laboratorio')
    asunto = 'Envío de solicitud de máquina'
    usuario = Usuario.objects.get(nombre_usuario = request.user.username)
    to = [request.user.email]
    context = {'asistente'     : usuario.nombre_completo(),
               'maquina_nombre': maquina_nombre,
               'solicitud_id'  : solicitud_id}
    template_path = os.path.join(BASE_DIR, 'templates', 'correos', 'solicitud_maquina_asistente.txt')
    # Enviar correo al asistente
    enviar_correo(asunto, EMAIL_HOST_USER, to, template_path, '', context)
    # Enviar correo a los jefes
    if jefes_lab.exists():
        template_path = os.path.join(BASE_DIR, 'templates', 'correos', 'solicitud_maquina_jefe.txt')
        to = []
        for jefe in jefes_lab:
            to.append(jefe.email)
        enviar_correo(asunto, EMAIL_HOST_USER, to, template_path, '', context)


def maquina_request(request, pk, template_name = 'maquinas/solicitar.html'):
    """Realiza la solicitud de máquinas por el usuario que la necesita
        Historia de usuario: ALF-4:Yo como Asistente de Laboratorio quiero solicitar una Maquina normal en una
        franja de tiempo especifica para hacer uso de ella
        Se encarga de:
            * Comprobar si hay un usuario logueado
            * Comprobar si el usuario tiene permisos para realizar la solicitud de máquinas
            * Realizar la solicitud de máquinas
     :param request: El HttpRequest que se va a responder.
     :type request: HttpRequest.
     :returns: HttpResponse -- La respuesta a la petición. Si no esta autorizado se envia un código 401
    """
    if request.user.is_authenticated() and request.user.has_perm("LabModule.can_requestMachine"):
        mensaje = 'ok'
        section = {'title': 'Solicitar Máquina'}
        try:
            inst_maquina = get_object_or_404(Maquina, pk = pk)
            inst_mueble = inst_maquina.mueble
            inst_ubicacion = get_object_or_404(MuebleEnLab, idMueble = inst_mueble)
            inst_profile = Usuario.objects.get(user_id = request.user.id)

            list_proyectos = Proyecto.objects.filter(asistentes = inst_profile.id,
                                                     activo = True)

            form = SolicitudForm()
            start = inst_maquina.fechaInicialDisp.strftime("%Y-%m-%d")
            end = inst_maquina.fechaFinalDisp.strftime("%Y-%m-%d")
            if request.method == 'POST':
                if form.verificar_fecha(inst_maquina.pk,
                                        request.POST['fechaInicial'],
                                        request.POST['fechaFinal']) == True:
                    if form.verificarDisponibilidad(start,end,request.POST['fechaInicial'],request.POST['fechaFinal'])==True:
                        requestObj = Solicitud()
                        requestObj.descripcion = 'Solicitud de Maquina'
                        requestObj.fechaInicial = request.POST['fechaInicial']
                        requestObj.fechaFinal = request.POST['fechaFinal']



                        if inst_maquina.con_reserva == True:
                            requestObj.estado = 'creada'
                        else:
                            requestObj.estado = 'aprobada'

                        requestObj.solicitante = inst_profile
                        requestObj.paso = Paso.objects.get(id = request.POST['step'])
                        requestObj.save()

                        maquinaRequest = SolicitudMaquina()
                        maquinaRequest.maquina = inst_maquina
                        maquinaRequest.solicitud = requestObj
                        maquinaRequest.save()

                        messages.success(request, "La máquina se reservó exitosamente")

                        # Envío de notificación
                        notificacion_solicitud_maquina(request, inst_mueble.nombre, maquinaRequest.id)

                        return redirect(reverse('maquina-detail', kwargs = {'pk': pk}))
                    else:
                        mensaje="Las fechas de solicitud estan por fuera de las fechas de disponibilidad"
                else:
                    mensaje = "Ya existe una solicitud para estas fechas"

            contexto = {'section'       : section,
                        'form'          : form,
                        'mensaje'       : mensaje,
                        'maquina'       : inst_maquina,
                        'mueble'        : inst_mueble,
                        'list_proyectos': list_proyectos,
                        'inst_ubicacion': inst_ubicacion,
                        'start'         : request.GET.get('start', ''),
                        'end'           : request.GET.get('end', '')}

        except ObjectDoesNotExist:
            contexto = {'mensaje': 'No hay máquinas o pasos con el id solicitado'}
        except MultipleObjectsReturned:
            contexto = {'mensaje': 'Muchas máquinas con ese id'}

        return render(request, template_name, contexto)
    else:
        return HttpResponse('No autorizado', status = 401)


def comprobarPostMaquina(form, formMaquina, formPos, request, template_name, section):
    """Desplegar y comprobar los valores a insertar.
        Historia de usuario: `ALF-18 <http://miso4101-2.virtual.uniandes.edu.co:8080/browse/ALF-18 />`_ :
        Yo como Jefe de Laboratorio quiero poder agregar nuevas máquinas en el sistema para que puedan ser usadas por los asistentes.
        Se encarga de:
            * Mostar el formulario para agregar una máquina.
            * Mostar el formulario para editar una máquina ya existente.
            * Agregar una máquina a la base de datos, agregar la relación entre la máquina y el
            laboratorio en el que está.
     :param form: La información relevante de la máquina.
     :type form: MaquinaForm.
     :param formPos: La posición y el laboratorio en el que se va a guardar la máquina.
     :type formPos: PosicionesMaquinaForm.
     :param request: El HttpRequest que se va a responder.
     :type request: HttpRequest.
     :param template_name: La template sobre la cual se va a renderizar.
     :type template_name: html.
     :param section: Objeto que permite diferenciar entre la modificación de una máquina y la adición de esta.
     :type section: {‘title’:,’agregar’}.
     :returns: HttpResponse -- La respuesta a la petición, en caso de que todo salga bien redirecciona a la
      modificación de la nueva máquina. Sino redirecciona al mismo formulario mostrand los errores.
    """
    mensaje = ""

    if form.is_valid() and formPos.is_valid() and formMaquina.is_valid():

        new_furniture = form.save(commit = False)
        new_furniture.tipo = 'maquina'
        new_machine = formMaquina.save(commit = False)
        new_machine_loc = formPos.save(commit = False)

        idLaboratorio = formPos.cleaned_data['idLaboratorio']
        posX = formPos.cleaned_data['posX']
        posY = formPos.cleaned_data['posY']

        es_ubicacion_libre = formPos.es_ubicacion_libre()

        if section['agregar'] and not es_ubicacion_libre:
           messages.error(request, "El lugar en el que desea guadar ya esta ocupado", extra_tags = "danger")
        else:
            if not section['agregar'] and not formPos.es_el_mismo_mueble(new_furniture.id,
                                                                         idLaboratorio,
                                                                         posX,
                                                                         posY) \
                    and not es_ubicacion_libre:
                messages.error(request, "El lugar en el que desea guadar ya esta ocupado", extra_tags="danger")
            else:
                if not formPos.es_ubicacion_rango(posX, posY):
                    if 'posX' in formPos.errors and formPos.errors['posX'] is not None \
                            and formPos.errors['posX'][0] == 'La columna ya esta ocupada':
                        del formPos.errors['posX'][0]

                    if 'posY' in formPos.errors and formPos.errors['posY'] is not None \
                            and formPos.errors['posY'][0] == 'La fila ya esta ocupada':
                        del formPos.errors['posY'][0]

                    mensaje = "La posición [" + \
                              str(new_machine_loc.posX) + "," + \
                              str(new_machine_loc.posY) + "] no se encuentra en el rango del laboratorio"
                    messages.error(request, mensaje, extra_tags="danger")
                else:
                    new_furniture.save()
                    new_machine.mueble = new_furniture
                    new_machine.save()
                    new_machine_loc.idMueble = new_furniture
                    new_machine_loc.save()

                    if section['agregar']:
                        messages.success(request, "La máquina se añadió exitosamente")
                    else:
                        messages.success(request, "La máquina se actualizó correctamente")
                    return redirect(reverse('maquina-detail', kwargs={'pk': new_machine.pk}))
    context = {'form'       : form,
               'formMaquina': formMaquina,
               'formPos'    : formPos,
               'mensaje'    : mensaje,
               'section'    : section,
               'start': request.GET.get('start', ''),
               'end': request.GET.get('end', '')
               }
    return render(request, template_name, context)
