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
                'placeholder': 'Nombre y Apellido',
                'maxlength': '50',
                'minlength': '3',
                'autocomplete': 'name'
            }),

            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12.345.678-5',
                'maxlength': '12',
                'minlength': '8',
                'oninput': "let v=this.value.toUpperCase().replace(/[^0-9K.-]/g,'');let d=(v.match(/[0-9]/g)||[]).length;if(d<7){v=v.replace(/K/g,'');}else{v=v.replace(/K(?=[0-9.-])/g,'');let i=v.indexOf('K');if(i!==-1)v=v.slice(0,i+1);}this.value=v;"
            }),

            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '912345678',
                'maxlength': '9',
                'minlength': '9',
                'inputmode': 'numeric',
                'autocomplete': 'tel',
                'oninput': "this.value = this.value.replace(/[^0-9]/g, '');"
            }),

            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.cl',
                'maxlength': '60',
                'autocomplete': 'email'
            }),

            'sueldo_mensual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '50000000',
                'step': '1',
                'placeholder': 'Ej: 750000',
                'oninput': "if(this.value.length > 8) this.value = this.value.slice(0, 8);"
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
                'Línea de Crédito: disponible desde $900.000. '
                'Tope máximo: $50.000.000.'
            ),

            'tipo_cuenta': (
                'Selecciona el producto que deseas solicitar.'
            ),
        }

        error_messages = {
            'titular': {
                'max_length': 'El nombre no puede superar los 50 caracteres.',
                'min_length': 'El nombre debe tener al menos 3 caracteres.',
            },
            'correo': {
                'max_length': 'El correo no puede superar los 60 caracteres.',
                'invalid': 'Ingrese una dirección de correo válida.',
            },
            'sueldo_mensual': {
                'max_value': 'La renta mensual no puede superar los $50.000.000 CLP.',
                'min_value': 'La renta mensual no puede ser negativa.',
            },
        }

    def clean_titular(self):
        titular = self.cleaned_data.get('titular', '').strip()
        if len(titular) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        if len(titular) > 50:
            raise forms.ValidationError('El nombre no puede superar los 50 caracteres.')
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'-]+$", titular):
            raise forms.ValidationError('El nombre solo debe contener letras y espacios.')
        partes = titular.split()
        if len(partes) < 2:
            raise forms.ValidationError('Ingrese al menos un nombre y un apellido.')
        return titular.title()

    def clean_correo(self):
        correo = self.cleaned_data.get('correo', '').strip().lower()
        if len(correo) < 5:
            raise forms.ValidationError('El correo debe tener al menos 5 caracteres.')
        if len(correo) > 60:
            raise forms.ValidationError('El correo no puede superar los 60 caracteres.')
        patron_correo = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(patron_correo, correo):
            raise forms.ValidationError('Ingrese un formato de correo válido (ej: usuario@ejemplo.cl).')
        if CuentaBancaria.objects.filter(correo=correo).exists():
            raise forms.ValidationError('Este correo ya se encuentra registrado.')
        if User.objects.filter(email=correo).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo.')
        return correo

    def clean_sueldo_mensual(self):
        sueldo = self.cleaned_data.get('sueldo_mensual')
        if sueldo is None:
            return 0
        if sueldo < 0:
            raise forms.ValidationError('La renta mensual no puede ser negativa.')
        if sueldo > 50000000:
            raise forms.ValidationError('La renta mensual no puede superar los $50.000.000 CLP.')
        return sueldo


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
                'maxlength': '50',
                'minlength': '3'
            }),

            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '12',
                'minlength': '8',
                'oninput': "let v=this.value.toUpperCase().replace(/[^0-9K.-]/g,'');let d=(v.match(/[0-9]/g)||[]).length;if(d<7){v=v.replace(/K/g,'');}else{v=v.replace(/K(?=[0-9.-])/g,'');let i=v.indexOf('K');if(i!==-1)v=v.slice(0,i+1);}this.value=v;"
            }),

            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '9',
                'minlength': '9',
                'inputmode': 'numeric',
                'oninput': "this.value = this.value.replace(/[^0-9]/g, '');"
            }),

            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'maxlength': '60'
            }),

            'sueldo_mensual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '50000000',
                'step': '1',
                'oninput': "if(this.value.length > 8) this.value = this.value.slice(0, 8);"
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
                'Línea de Crédito: mínimo $900.000. '
                'Tope máximo: $50.000.000.'
            ),
        }

        error_messages = {
            'titular': {
                'max_length': 'El nombre no puede superar los 50 caracteres.',
                'min_length': 'El nombre debe tener al menos 3 caracteres.',
            },
            'correo': {
                'max_length': 'El correo no puede superar los 60 caracteres.',
                'invalid': 'Ingrese una dirección de correo válida.',
            },
            'sueldo_mensual': {
                'max_value': 'La renta mensual no puede superar los $50.000.000 CLP.',
                'min_value': 'La renta mensual no puede ser negativa.',
            },
        }

    def clean_titular(self):
        titular = self.cleaned_data.get('titular', '').strip()
        if len(titular) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        if len(titular) > 50:
            raise forms.ValidationError('El nombre no puede superar los 50 caracteres.')
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'-]+$", titular):
            raise forms.ValidationError('El nombre solo debe contener letras y espacios.')
        partes = titular.split()
        if len(partes) < 2:
            raise forms.ValidationError('Ingrese al menos un nombre y un apellido.')
        return titular.title()

    def clean_correo(self):
        correo = self.cleaned_data.get('correo', '').strip().lower()
        if len(correo) < 5:
            raise forms.ValidationError('El correo debe tener al menos 5 caracteres.')
        if len(correo) > 60:
            raise forms.ValidationError('El correo no puede superar los 60 caracteres.')
        patron_correo = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(patron_correo, correo):
            raise forms.ValidationError('Ingrese un formato de correo válido (ej: usuario@ejemplo.cl).')
        existe_cuenta = CuentaBancaria.objects.filter(correo=correo).exclude(pk=self.instance.pk).exists()
        if existe_cuenta:
            raise forms.ValidationError('Este correo ya se encuentra registrado en otra cuenta.')
        return correo

    def clean_sueldo_mensual(self):
        sueldo = self.cleaned_data.get('sueldo_mensual')
        if sueldo is None:
            return 0
        if sueldo < 0:
            raise forms.ValidationError('La renta mensual no puede ser negativa.')
        if sueldo > 50000000:
            raise forms.ValidationError('La renta mensual no puede superar los $50.000.000 CLP.')
        return sueldo


# =========================================================
# REGISTRO DE CLIENTE
# =========================================================

class RegistroClienteForm(forms.Form):

    titular = forms.CharField(
        max_length=50,
        min_length=3,
        label='Nombre completo',
        error_messages={
            'max_length': 'El nombre no puede superar los 50 caracteres.',
            'min_length': 'El nombre debe tener al menos 3 caracteres.',
            'required': 'Ingrese su nombre completo.'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre y Apellido',
            'maxlength': '50',
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
            'autocomplete': 'username',
            'oninput': "let v=this.value.toUpperCase().replace(/[^0-9K.-]/g,'');let d=(v.match(/[0-9]/g)||[]).length;if(d<7){v=v.replace(/K/g,'');}else{v=v.replace(/K(?=[0-9.-])/g,'');let i=v.indexOf('K');if(i!==-1)v=v.slice(0,i+1);}this.value=v;"
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
            'autocomplete': 'tel',
            'oninput': "this.value = this.value.replace(/[^0-9]/g, '');"
        })
    )

    correo = forms.EmailField(
        max_length=60,
        label='Correo electrónico',
        error_messages={
            'max_length': 'El correo no puede superar los 60 caracteres.',
            'invalid': 'Ingrese una dirección de correo válida.',
            'required': 'Ingrese su correo electrónico.'
        },
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.cl',
            'maxlength': '60',
            'autocomplete': 'email'
        })
    )

    sueldo_mensual = forms.DecimalField(
        min_value=0,
        max_value=50000000,
        decimal_places=0,
        max_digits=12,
        label='Renta mensual',
        error_messages={
            'max_value': 'La renta mensual no puede superar los $50.000.000 CLP.',
            'min_value': 'La renta mensual no puede ser negativa.',
            'max_digits': 'El monto excede el número de dígitos permitido.',
            'required': 'Ingrese su renta mensual.'
        },
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 750000',
            'min': '0',
            'max': '50000000',
            'step': '1',
            'oninput': "if(this.value.length > 8) this.value = this.value.slice(0, 8);"
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

        if len(titular) > 50:
            raise forms.ValidationError(
                'El nombre no puede superar los 50 caracteres.'
            )

        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'-]+$", titular):
            raise forms.ValidationError(
                'El nombre solo debe contener letras y espacios.'
            )

        partes = titular.split()
        if len(partes) < 2:
            raise forms.ValidationError(
                'Ingrese al menos un nombre y un apellido.'
            )

        return titular.title()


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

        if len(correo) < 5:
            raise forms.ValidationError(
                'El correo debe tener al menos 5 caracteres.'
            )

        if len(correo) > 60:
            raise forms.ValidationError(
                'El correo no puede superar los 60 caracteres.'
            )

        patron_correo = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(patron_correo, correo):
            raise forms.ValidationError(
                'Ingrese un formato de correo válido (ej: usuario@ejemplo.cl).'
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

        if sueldo > 50000000:

            raise forms.ValidationError(
                'La renta mensual no puede superar los $50.000.000 CLP.'
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