import re

from django import forms
from django.contrib.auth.models import User

from .models import (
    CuentaBancaria,
    normalizar_rut,
    validar_rut_chileno,
)


# =========================================================
# CREAR CUENTA
# =========================================================

class CrearCuentaForm(forms.ModelForm):

    class Meta:

        model = CuentaBancaria

        fields = [
            'titular',
            'rut',
            'telefono',
            'correo',
            'sueldo_mensual',
            'tipo_cuenta',
        ]

        widgets = {

            'titular': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo',
                'maxlength': '100',
                'minlength': '3',
                'autocomplete': 'name'
            }),

            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12.345.678-5',
                'maxlength': '12',
                'minlength': '8'
            }),

            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '912345678',
                'maxlength': '9',
                'minlength': '9',
                'inputmode': 'numeric',
                'autocomplete': 'tel'
            }),

            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.cl',
                'maxlength': '150',
                'autocomplete': 'email'
            }),

            'sueldo_mensual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '999999999999',
                'step': '1',
                'placeholder': 'Ej: 750000'
            }),

            'tipo_cuenta': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

        help_texts = {

            'rut': (
                'Se validará el dígito verificador y '
                'el RUT no puede estar registrado anteriormente.'
            ),

            'telefono': (
                'Ingrese un celular chileno de 9 dígitos. '
                'Ejemplo: 912345678.'
            ),

            'sueldo_mensual': (
                'Cuenta Débito: sin renta mínima. '
                'Cuenta Corriente: mínimo $600.000. '
                'Línea de Crédito: disponible desde $900.000.'
            ),

            'tipo_cuenta': (
                'Selecciona el producto que deseas solicitar.'
            ),
        }


# =========================================================
# EDITAR CUENTA
# =========================================================

class EditarCuentaForm(forms.ModelForm):

    class Meta:

        model = CuentaBancaria

        fields = [
            'titular',
            'rut',
            'telefono',
            'correo',
            'sueldo_mensual',
            'tipo_cuenta',
            'saldo',
            'estado',
        ]

        widgets = {

            'titular': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100',
                'minlength': '3'
            }),

            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '12',
                'minlength': '8'
            }),

            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '9',
                'minlength': '9',
                'inputmode': 'numeric'
            }),

            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'maxlength': '150'
            }),

            'sueldo_mensual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '999999999999',
                'step': '1'
            }),

            'tipo_cuenta': forms.Select(attrs={
                'class': 'form-select'
            }),

            'saldo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '99999999999999',
                'step': '1'
            }),

            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

        help_texts = {

            'rut': (
                'Debe corresponder a un RUT chileno válido '
                'y no puede pertenecer a otra cuenta.'
            ),

            'telefono': (
                'Celular chileno de 9 dígitos.'
            ),

            'sueldo_mensual': (
                'Cuenta Corriente: mínimo $600.000. '
                'Línea de Crédito: mínimo $900.000.'
            ),
        }


# =========================================================
# REGISTRO DE CLIENTE
# =========================================================

class RegistroClienteForm(forms.Form):

    titular = forms.CharField(
        max_length=100,
        min_length=3,
        label='Nombre completo',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre completo',
            'maxlength': '100',
            'minlength': '3',
            'autocomplete': 'name'
        })
    )

    rut = forms.CharField(
        max_length=12,
        min_length=8,
        label='RUT',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12.345.678-5',
            'maxlength': '12',
            'minlength': '8',
            'autocomplete': 'username'
        })
    )

    telefono = forms.CharField(
        max_length=9,
        min_length=9,
        label='Teléfono',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '912345678',
            'maxlength': '9',
            'minlength': '9',
            'inputmode': 'numeric',
            'autocomplete': 'tel'
        })
    )

    correo = forms.EmailField(
        max_length=150,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.cl',
            'maxlength': '150',
            'autocomplete': 'email'
        })
    )

    sueldo_mensual = forms.DecimalField(
        min_value=0,
        max_value=999999999999,
        decimal_places=0,
        max_digits=12,
        label='Renta mensual',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 750000',
            'min': '0',
            'max': '999999999999',
            'step': '1'
        })
    )

    tipo_cuenta = forms.ChoiceField(
        choices=CuentaBancaria.TIPOS_CUENTA,
        label='Tipo de cuenta',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    password1 = forms.CharField(
        min_length=6,
        max_length=10,
        label='Contraseña',
        help_text=(
            'Entre 6 y 10 caracteres. '
            'Debe incluir al menos una letra, '
            'un número y un símbolo.'
        ),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Banco1!',
            'minlength': '6',
            'maxlength': '10',
            'autocomplete': 'new-password'
        })
    )

    password2 = forms.CharField(
        min_length=6,
        max_length=10,
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repita la contraseña',
            'minlength': '6',
            'maxlength': '10',
            'autocomplete': 'new-password'
        })
    )


    # -----------------------------------------------------
    # VALIDAR NOMBRE
    # -----------------------------------------------------

    def clean_titular(self):

        titular = self.cleaned_data['titular'].strip()

        if len(titular) < 3:

            raise forms.ValidationError(
                'El nombre debe tener al menos 3 caracteres.'
            )

        return titular


    # -----------------------------------------------------
    # VALIDAR RUT
    # -----------------------------------------------------

    def clean_rut(self):

        rut = self.cleaned_data['rut']

        validar_rut_chileno(rut)

        rut_normalizado = normalizar_rut(rut)

        if CuentaBancaria.objects.filter(
            rut=rut_normalizado
        ).exists():

            raise forms.ValidationError(
                'Este RUT ya tiene una cuenta registrada.'
            )

        if User.objects.filter(
            username=rut_normalizado
        ).exists():

            raise forms.ValidationError(
                'Ya existe un usuario registrado con este RUT.'
            )

        return rut_normalizado


    # -----------------------------------------------------
    # VALIDAR TELÉFONO
    # -----------------------------------------------------

    def clean_telefono(self):

        telefono = self.cleaned_data['telefono']

        if not telefono.isdigit():

            raise forms.ValidationError(
                'El teléfono debe contener solamente números.'
            )

        if len(telefono) != 9:

            raise forms.ValidationError(
                'El teléfono debe tener exactamente 9 dígitos.'
            )

        if not telefono.startswith('9'):

            raise forms.ValidationError(
                'El celular debe comenzar con 9.'
            )

        return telefono


    # -----------------------------------------------------
    # VALIDAR CORREO
    # -----------------------------------------------------

    def clean_correo(self):

        correo = (
            self.cleaned_data['correo']
            .strip()
            .lower()
        )

        if len(correo) > 150:

            raise forms.ValidationError(
                'El correo no puede superar los 150 caracteres.'
            )

        if CuentaBancaria.objects.filter(
            correo=correo
        ).exists():

            raise forms.ValidationError(
                'Este correo ya se encuentra registrado.'
            )

        if User.objects.filter(
            email=correo
        ).exists():

            raise forms.ValidationError(
                'Ya existe un usuario con este correo.'
            )

        return correo


    # -----------------------------------------------------
    # VALIDAR RENTA
    # -----------------------------------------------------

    def clean_sueldo_mensual(self):

        sueldo = self.cleaned_data['sueldo_mensual']

        if sueldo < 0:

            raise forms.ValidationError(
                'La renta mensual no puede ser negativa.'
            )

        if sueldo > 999999999999:

            raise forms.ValidationError(
                'La renta mensual supera el máximo permitido.'
            )

        return sueldo


    # -----------------------------------------------------
    # VALIDAR CONTRASEÑA
    # -----------------------------------------------------

    def clean_password1(self):

        password = self.cleaned_data['password1']

        if len(password) < 6 or len(password) > 10:

            raise forms.ValidationError(
                'La contraseña debe tener entre 6 y 10 caracteres.'
            )

        # Al menos una letra
        if not re.search(r'[A-Za-z]', password):

            raise forms.ValidationError(
                'La contraseña debe contener al menos una letra.'
            )

        # Al menos un número
        if not re.search(r'\d', password):

            raise forms.ValidationError(
                'La contraseña debe contener al menos un número.'
            )

        # Al menos un símbolo
        if not re.search(
            r'[!@#$%^&*()_\-+=\[\]{};:,.?]',
            password
        ):

            raise forms.ValidationError(
                'La contraseña debe contener al menos un símbolo. '
                'Ejemplo: ! @ # $ %'
            )

        return password


    # -----------------------------------------------------
    # VALIDACIONES GENERALES
    # -----------------------------------------------------

    def clean(self):

        datos = super().clean()

        password1 = datos.get('password1')
        password2 = datos.get('password2')

        tipo_cuenta = datos.get('tipo_cuenta')
        sueldo_mensual = datos.get('sueldo_mensual')


        # ---------------------------------------------
        # CONFIRMAR CONTRASEÑA
        # ---------------------------------------------

        if password1 and password2:

            if password1 != password2:

                self.add_error(
                    'password2',
                    'Las contraseñas no coinciden.'
                )


        # ---------------------------------------------
        # CUENTA CORRIENTE
        # ---------------------------------------------

        if (
            tipo_cuenta == 'CORRIENTE'
            and sueldo_mensual is not None
            and sueldo_mensual
            < CuentaBancaria.RENTA_MIN_CORRIENTE
        ):

            self.add_error(
                'sueldo_mensual',
                'Para abrir una Cuenta Corriente '
                'se requiere una renta mensual '
                'mínima de $600.000.'
            )

        return datos