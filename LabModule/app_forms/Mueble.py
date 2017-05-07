# -*- coding: utf-8 -*-
from django.forms import ModelForm

from LabModule.app_models.Mueble import Mueble
from LabModule.app_models.MuebleEnLab import MuebleEnLab
from LabModule.app_models.Laboratorio import Laboratorio


class MuebleForm(ModelForm):
    """Formulario  para crear y modificar el lugar almacenamiento.
           Se encarga de:
               * Tener una instancia del modelo del lugar almacenamiento en laboraotrio.
               * Agregar un lugar almacenamiento a la base de datos.
               * Modificar un lugar almacenamiento ya existente.
        :param ModelForm: Instancia de Django.forms.
        :type ModelForm: ModelForm.
       """

    class Meta:
        model = Mueble
        fields = [ 'nombre', 'descripcion', 'estado', 'imagen']
        exclude=('tipo',)

class PosicionesMuebleForm(ModelForm):
    """Formulario  para crear y modificar la ubicación de un lugar almacenamiento.
        Se encarga de:
            * Tener una instancia del modelo del lugar almacenamiento en laboratorio.
            * Definir las posición x, la posición y y el laboratorio en el cual se va aguardar el lugar almacenamiento.
            * Agregar un lugar almacenamiento a la base de datos, agregar la relación entre el lugar almacenamiento y el laboratorio en el que está.
            * Modificar la ubicación de un lugar almacenamiento ya existente.
     :param ModelForm: Instancia de Django.forms.
     :type ModelForm: ModelForm.
    """

    class Meta:
        model = MuebleEnLab
        fields = ['idLaboratorio', 'posX', 'posY']
        exclude = ('idMueble',)

    def es_ubicacion_libre(self):
        if MuebleEnLab.es_ubicacion_libre(self.cleaned_data['idLaboratorio'],self.cleaned_data['posX'], self.cleaned_data['posY']):
            return True
        else:
            self.add_error('posX', "La columna  ya esta ocupada")
            self.add_error('posY', "La fila ya esta ocupada")

        return False

    def es_ubicacion_rango(self):
        lab = self.cleaned_data['idLaboratorio']
        masX = lab.numX >= self.cleaned_data['posX']
        masY = lab.numY >= self.cleaned_data['posY']
        posible = masX and masY
        if not posible:
            if not masX:
                self.add_error("posX", "La columna sobrepasa el valor máximo de " + str(lab.numX))
            if not masY:
                self.add_error("posY", "La fila y sobrepasa el valor máximo de " + str(lab.numY))
            return False
        return True
