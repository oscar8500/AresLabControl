# -*- coding: utf-8 -*-
import json

from django.contrib import messages
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from LabModule.app_forms.Almacenamiento import AlmacenamientoForm
from LabModule.app_forms.Mueble import MuebleForm
from LabModule.app_forms.Mueble import PosicionesMuebleForm
from LabModule.app_models.Almacenamiento import Almacenamiento
from LabModule.app_models.Bandeja import Bandeja
from LabModule.app_models.MuebleEnLab import MuebleEnLab
from LabModule.app_models.MuestraEnBandeja import MuestraEnBandeja
from LabModule.app_utils.cursores import *


def lugar_add(request, template_name='almacenamientos/agregar.html'):
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
    if request.user.is_authenticated() and request.user.has_perm("LabModule.can_addStorage"):
        section = {'title': 'Agregar Almacenamiento', 'agregar': True}
        mensaje = ""
        form = MuebleForm(request.POST or None, request.FILES or None)
        formAlmacenamiento = AlmacenamientoForm(request.POST or None, request.FILES or None)
        formPos = PosicionesMuebleForm(request.POST or None, request.FILES or None)
        if request.method == 'POST':
            return comprobarPostLugar(form, formAlmacenamiento, formPos, request, template_name, section)
        context = {'form': form,
                   'formAlmacenamiento': formAlmacenamiento,
                   'formPos': formPos,
                   'mensaje': mensaje,
                   'section': section}
        return render(request, template_name, context)
    else:
        return HttpResponse('No autorizado', status=401)


def lugar_detail(request, pk, template_name='almacenamientos/detalle.html'):
    """Desplegar y comprobar los valores a consultar.
                Historia de usuario: ALF-42-Yo como Jefe de Laboratorio quiero poder ver el detalle de un
                lugar de almacenamiento para conocer sus características
                Se encarga de:
                * Mostar el formulario para consultar los lugares de almacenamiento.
            :param request: El HttpRequest que se va a responder.
            :type request: HttpRequest.
            :param pk: La llave primaria del lugar de almacenamiento
            :type pk: String.
            :returns: HttpResponse -- La respuesta a la petición, con información de los lugares de almacenamiento existentes.
        """
    if request.user.is_authenticated() and request.user.has_perm("LabModule.can_viewSample"):
        section = {'title': 'Ver Detalle ', 'agregar': "ver"}

        lugar = get_object_or_404(Almacenamiento, pk=pk)
        mueble = lugar.mueble
        laboratorio = MuebleEnLab.get_laboratorio(mueble)

        bandejas = [bandeja.id for bandeja in Bandeja.objects.filter(almacenamiento=lugar)]
        espaciosOcupados = len([m for m in MuestraEnBandeja.objects.filter(idBandeja__in=bandejas)])
        espacioslibres = lugar.get_max_capacidad() - espaciosOcupados

        pos = MuebleEnLab.objects.get(idLaboratorio=laboratorio,
                                      idMueble=mueble)

        context = {'lugar': lugar,
                   'espaciosOcupados': espaciosOcupados,
                   'espacioslibres': espacioslibres,
                   'laboratorio': laboratorio,
                   'mueble': mueble,
                   'pos': pos,
                   'section': section}
        return render(request, template_name, context)
    else:
        return HttpResponse('No autorizado', status=401)


def lugar_update(request, pk, template_name='almacenamientos/agregar.html'):
    if request.user.is_authenticated() and request.user.has_perm("LabModule.can_editStorage"):
        section = {'title': 'Modificar Lugar de Almacenamiento', 'agregar': False}

        inst_almacenamiento = get_object_or_404(Almacenamiento, pk=pk)
        inst_mueble = inst_almacenamiento.mueble
        inst_ubicacion = get_object_or_404(MuebleEnLab, idMueble=inst_mueble)

        form = MuebleForm(request.POST or None,
                          request.FILES or None,
                          instance=inst_mueble)
        formAlmacenamiento = AlmacenamientoForm(request.POST or None,
                                                request.FILES or None,
                                                instance=inst_almacenamiento)
        formPos = PosicionesMuebleForm(request.POST or None,
                                       request.FILES or None,
                                       instance=inst_ubicacion)

        return comprobarPostLugar(form, formAlmacenamiento, formPos, request, template_name, section)
    else:
        return HttpResponse('No autorizado', status=401)


def lugar_list(request, template_name='almacenamientos/listar.html'):
    """Desplegar y comprobar los valores a consultar.
              Historia de usuario: ALF-39 - Yo como Jefe de Laboratorio quiero poder filtrar los lugares de
              almacenamiento existentes por nombre para visualizar sólo los que me interesan.
              Se encarga de:
                  * Mostar el formulario para consultar los lugares de almacenamiento.
           :param request: El HttpRequest que se va a responder.
           :type request: HttpRequest.
           :returns: HttpResponse -- La respuesta a la petición, con información de los lugares de
           almacenamiento existentes.
          """
    if request.user.is_authenticated() and request.user.has_perm("LabModule.can_listStorage"):
        section = {'title': 'Listar Almacenamientos'}
        can_editStorage = request.user.has_perm("LabModule.can_editStorage")
        lista_almacenamiento = obtener_lugares(not can_editStorage)

        context = {'section': section,
                   'lista_lugares': lista_almacenamiento}
        return render(request, template_name, context)
    else:
        return HttpResponse('No autorizado', status=401)


def comprobarPostLugar(form, formAlmacenamiento, formPos, request, template_name, section):
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
    if form.is_valid() and formPos.is_valid() and formAlmacenamiento.is_valid():

        new_furniture = form.save(commit=False)
        new_furniture.tipo = 'almacenamiento'
        new_storage = formAlmacenamiento.save(commit=False)
        new_storage_loc = formPos.save(commit=False)

        idLaboratorio = formPos.cleaned_data['idLaboratorio']
        posX = formPos.cleaned_data['posX']
        posY = formPos.cleaned_data['posY']

        es_ubicacion_libre = formPos.es_ubicacion_libre()

        if section['agregar'] and not es_ubicacion_libre:
            messages.error(request, "El lugar en el que desea guadar ya esta ocupado", extra_tags="danger")
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
                              str(new_storage_loc.posX) + "," + \
                              str(new_storage_loc.posY) + "] no se encuentra en el rango del laboratorio"
                    messages.error(request, mensaje, extra_tags="danger")
                else:
                    new_furniture.save()
                    new_storage.mueble = new_furniture
                    new_storage.save()
                    new_storage_loc.idMueble = new_furniture
                    new_storage_loc.save()

                    if section['agregar']:
                        messages.success(request, "El lugar de almacenamiento se añadió exitosamente")
                    else:
                        messages.success(request, "El lugar de almacenamiento se actualizó correctamente")
                    return redirect(reverse('lugar-detail', kwargs={'pk': new_storage.pk}))
    context = {'form': form,
               'formAlmacenamiento': formAlmacenamiento,
               'formPos': formPos,
               'mensaje': mensaje,
               'section': section,
               }
    return render(request, template_name, context)



def obtener_lugares(cannot_editStorage):
    """
    Obtiene los lugares de almacenamiento para filtrarlos por protocolo
    :param cannot_editStorage: Indica si puede o no editar los registros de almacanamiento
    :return: listado de lugares de almacenamiento
    """
    query = queryListaLugares

    if cannot_editStorage:
        query += ''' AND m.estado = true '''

    query += ''' ORDER BY 2'''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = dictfetchall(cursor)
    return rows
