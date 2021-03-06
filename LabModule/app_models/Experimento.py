# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

from LabModule.app_models.Protocolo import Protocolo
from LabModule.app_models.Proyecto import Proyecto

permissions_experiment = (
    ('can_addExperiment', 'experimento||agregar'),
    ('can_editExperiment', 'experimento||editar'),
    ('can_listExperiment', 'experimento||listar'),
    ('can_viewExperiment', 'experimento||ver'),
)


class Experimento(models.Model):
    """Representación de un experimento.
        Se encarga de:
            * Definir las caracteristicas de un experimento
            * Definir las restricciónes basicas de los campos
            * Permite guardar en la base de datos esta entidad

        Atributos:
            :nombre (String): Nombre expermento
            :descripción (String): descripción del experimento.
            :objetivo (String): Objetivo del experimento
            :proyecto (Decimal): Seleccion de Proyecto
            :protocolos (Object): Lista de protocolos
        Permisos:
            :can_addExperiment: Permite agregar experimento
            :can_editExperiment: Permite modificar experimento
            :can_viewExperiment: Permite ver experimento
    """

    class Meta:
        verbose_name = _('Experimento')
        verbose_name_plural = _('Experimentos')
        app_label = 'LabModule'
        permissions = permissions_experiment

    nombre = models.CharField(
            max_length = 50,
            blank = False,
            null = True,
            verbose_name = _("Nombre Expermento")
    )
    descripcion = models.TextField(
            max_length = 200,
            blank = False,
            null = True,
            verbose_name = _("Descripción del Experimento")
    )
    objetivo = models.TextField(
            max_length = 200,
            blank = False,
            null = True,
            verbose_name = _("Objetivo del Experimento")
    )
    proyecto = models.ForeignKey(
            Proyecto,
            blank = False,
            null = True,
            on_delete = models.CASCADE,
            verbose_name = _("Proyecto"),
            related_name = '%(app_label)s_%(class)s_related'
    )
    protocolos = models.ManyToManyField(
            Protocolo,
            verbose_name = "Protocolos",
            related_name = '%(app_label)s_%(class)s_related'
    )

    def __unicode__(self):
        return self.nombre.capitalize()
