# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm

from LabModule.app_models.Muestra import Muestra
from LabModule.app_models.SolicitudMuestra import SolicitudMuestra

class MuestraForm(ModelForm):
    """Formulario  para crear y modificar muestras.
           Se encarga de:
               * Tener una instancia del modelo muestra.
               * Agregar una muestra a la base de datos.
               * Modificar una muestra ya existente.
        :param ModelForm: Instancia de Django.forms.
        :type ModelForm: ModelForm.
       """

    class Meta:
        model = Muestra
        fields = ['nombre', 'descripcion', 'imagen']


class MuestraSolicitudForm(ModelForm):
    class Meta:
        model = SolicitudMuestra
        fields = ['cantidad', 'solicitud', 'muestra', 'tipo']
        widgets = {
            'cantidad': forms.TextInput(attrs = {'class': 'form-control'})
        }


class MuestraAddForm(forms.Form):
  def __init__(self, *args, **kwargs):
    maxi = kwargs.pop('maximo')
    super(MuestraAddForm, self).__init__(*args, **kwargs)
    self.fields['cantidad'] = forms.IntegerField(label="Cantidad", max_value=maxi,min_value=1)