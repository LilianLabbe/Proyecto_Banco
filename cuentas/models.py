from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from datetime import date
from decimal import Decimal
import secrets


# =========================================================
# VALIDACIÓN DE RUT CHILENO
# =========================================================

def validar_rut_chileno(rut):
    """
    Valida matemáticamente un RUT chileno mediante módulo 11.

    Acepta:
    12.345.678-5
    12345678-5
    123456785
    """

    if not rut:
        raise ValidationError("Ingrese un RUT válido.")

    rut_limpio = (
        rut.replace(".", "")
        .replace("-", "")
        .replace(" ", "")
        .upper()
    )

    if len(rut_limpio) < 2:
        raise ValidationError("Ingrese un RUT válido.")

    cuerpo = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]

    if not cuerpo.isdigit():
        raise ValidationError(
            "El RUT contiene caracteres inválidos."
        )

    suma = 0
    multiplicador = 2

    for numero in reversed(cuerpo):

        suma += int(numero) * multiplicador

        multiplicador += 1

        if multiplicador == 8:
            multiplicador = 2

    resto = 11 - (suma % 11)

    if resto == 11:
        dv_calculado = "0"

    elif resto == 10:
        dv_calculado = "K"

    else:
        dv_calculado = str(resto)

    if dv_ingresado != dv_calculado:

        raise ValidationError(
            "El RUT ingresado no es válido. "
            "Revise el dígito verificador."
        )


# =========================================================
# NORMALIZAR RUT
# =========================================================

def normalizar_rut(rut):
    """
    Guarda siempre el RUT con formato:
    12.345.678-5
    """

    rut_limpio = (
        rut.replace(".", "")
        .replace("-", "")
        .replace(" ", "")
        .upper()
    )

    cuerpo = rut_limpio[:-1]
    dv = rut_limpio[-1]

    cuerpo_formateado = (
        f"{int(cuerpo):,}"
        .replace(",", ".")
    )

    return f"{cuerpo_formateado}-{dv}"


# =========================================================
# MODELO CUENTA BANCARIA
# =========================================================

class CuentaBancaria(models.Model):

    # =====================================================
    # REGLAS ACADÉMICAS DEL PROYECTO
    # =====================================================

    RENTA_MIN_CORRIENTE = Decimal("600000")
    RENTA_MIN_LINEA_CREDITO = Decimal("900000")
    RENTA_MIN_TARJETA_CREDITO = Decimal("1200000")

    # =====================================================
    # TIPOS DE CUENTA
    # =====================================================

    TIPOS_CUENTA = [
        ("DEBITO", "Cuenta Débito"),
        ("CORRIENTE", "Cuenta Corriente"),
    ]

    # =====================================================
    # ESTADOS DE LA CUENTA
    # =====================================================

    ESTADOS = [
        ("ACTIVA", "Activa"),
        ("BLOQUEADA", "Bloqueada"),
        ("CERRADA", "Cerrada"),
    ]

    # =====================================================
    # DATOS DE LA CUENTA
    # =====================================================

    numero_cuenta = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        blank=True,
        verbose_name="Número de cuenta"
    )

    # =====================================================
    # DATOS DEL CLIENTE
    # =====================================================

    titular = models.CharField(
        max_length=100,
        verbose_name="Nombre completo"
    )

    rut = models.CharField(
        max_length=12,
        unique=True,
        validators=[
            validar_rut_chileno
        ],
        verbose_name="RUT"
    )

    telefono = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r"^9\d{8}$",
                message=(
                    "Ingrese un celular chileno válido "
                    "de 9 dígitos. Ejemplo: 912345678"
                )
            )
        ],
        verbose_name="Teléfono"
    )

    correo = models.EmailField(
        max_length=150,
        unique=True,
        verbose_name="Correo electrónico"
    )

    sueldo_mensual = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        validators=[
            MinValueValidator(0)
        ],
        verbose_name="Renta mensual"
    )

    # =====================================================
    # PRODUCTO BANCARIO
    # =====================================================

    tipo_cuenta = models.CharField(
        max_length=20,
        choices=TIPOS_CUENTA,
        verbose_name="Producto solicitado"
    )

    saldo = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        default=0,
        validators=[
            MinValueValidator(0)
        ],
        verbose_name="Saldo disponible"
    )

    fecha_apertura = models.DateField(
        default=date.today,
        verbose_name="Fecha de apertura"
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="ACTIVA",
        verbose_name="Estado"
    )

    # =====================================================
    # TARJETA DE CRÉDITO
    # =====================================================

    tarjeta_credito_solicitada = models.BooleanField(
        default=False,
        verbose_name="Tarjeta de crédito solicitada"
    )

    # =====================================================
    # VALIDACIONES DE NEGOCIO
    # =====================================================

    def clean(self):

        super().clean()

        # ---------------------------------------------
        # RUT
        # ---------------------------------------------

        if self.rut:

            validar_rut_chileno(
                self.rut
            )

            # Lo normalizamos antes de validar
            # duplicados.
            self.rut = normalizar_rut(
                self.rut
            )

        # ---------------------------------------------
        # CUENTA CORRIENTE
        # ---------------------------------------------

        if (
            self.tipo_cuenta == "CORRIENTE"
            and self.sueldo_mensual
            < self.RENTA_MIN_CORRIENTE
        ):

            raise ValidationError({
                "sueldo_mensual":
                    "Para abrir una Cuenta Corriente "
                    "se requiere una renta mensual "
                    "mínima de $600.000."
            })

    # =====================================================
    # GENERAR NÚMERO DE CUENTA
    # =====================================================

    def generar_numero_cuenta(self):

        while True:

            numero = str(
                secrets.randbelow(
                    900_000_000_000
                )
                + 100_000_000_000
            )

            existe = (
                CuentaBancaria.objects
                .filter(
                    numero_cuenta=numero
                )
                .exists()
            )

            if not existe:
                return numero

    # =====================================================
    # GUARDAR
    # =====================================================

    def save(self, *args, **kwargs):

        # ---------------------------------------------
        # NORMALIZAR RUT
        # ---------------------------------------------

        if self.rut:

            self.rut = normalizar_rut(
                self.rut
            )

        # ---------------------------------------------
        # NORMALIZAR CORREO
        # ---------------------------------------------

        if self.correo:

            self.correo = (
                self.correo
                .strip()
                .lower()
            )

        # ---------------------------------------------
        # NORMALIZAR NOMBRE
        # ---------------------------------------------

        if self.titular:

            self.titular = (
                self.titular
                .strip()
                .title()
            )

        # ---------------------------------------------
        # GENERAR NÚMERO DE CUENTA
        # ---------------------------------------------

        if not self.numero_cuenta:

            self.numero_cuenta = (
                self.generar_numero_cuenta()
            )

        super().save(
            *args,
            **kwargs
        )

    # =====================================================
    # FORMATEO DE PESOS CHILENOS
    # =====================================================

    @staticmethod
    def formatear_pesos(valor):

        if valor is None:
            return "0"

        return (
            f"{int(valor):,}"
            .replace(",", ".")
        )

    @property
    def saldo_formateado(self):

        return self.formatear_pesos(
            self.saldo
        )

    @property
    def sueldo_formateado(self):

        return self.formatear_pesos(
            self.sueldo_mensual
        )

    # =====================================================
    # CUENTA DÉBITO
    # =====================================================

    @property
    def puede_cuenta_debito(self):

        return (
            self.estado == "ACTIVA"
        )

    # =====================================================
    # CUENTA CORRIENTE
    # =====================================================

    @property
    def tiene_cuenta_corriente(self):

        return (
            self.tipo_cuenta
            == "CORRIENTE"
        )

    @property
    def puede_cuenta_corriente(self):

        return (
            self.sueldo_mensual
            >= self.RENTA_MIN_CORRIENTE
            and self.estado == "ACTIVA"
        )

    @property
    def estado_cuenta_corriente(self):

        if self.estado != "ACTIVA":

            return (
                "La cuenta debe estar activa."
            )

        if self.tiene_cuenta_corriente:

            return (
                "Ya tienes una Cuenta Corriente."
            )

        if self.puede_cuenta_corriente:

            return (
                "Cumples los requisitos para "
                "optar a una Cuenta Corriente."
            )

        diferencia = (
            self.RENTA_MIN_CORRIENTE
            - self.sueldo_mensual
        )

        diferencia_formateada = (
            self.formatear_pesos(
                diferencia
            )
        )

        return (
            "Renta insuficiente. "
            f"Faltan ${diferencia_formateada}."
        )

    # =====================================================
    # LÍNEA DE CRÉDITO
    # =====================================================

    @property
    def tiene_linea_credito(self):
        """
        La Línea de Crédito solamente puede estar
        asociada a una Cuenta Corriente.
        """

        return (
            self.tipo_cuenta == "CORRIENTE"
            and self.sueldo_mensual
            >= self.RENTA_MIN_LINEA_CREDITO
            and self.estado == "ACTIVA"
        )

    @property
    def puede_linea_credito(self):
        """
        Alias para mantener compatibilidad
        con templates anteriores.
        """

        return self.tiene_linea_credito

    @property
    def estado_linea_credito(self):

        if self.estado != "ACTIVA":

            return (
                "La cuenta debe estar activa."
            )

        if self.tipo_cuenta != "CORRIENTE":

            return (
                "La Línea de Crédito está disponible "
                "únicamente para clientes que tengan "
                "una Cuenta Corriente."
            )

        if self.tiene_linea_credito:

            return (
                "Línea de Crédito incluida "
                "en tu Cuenta Corriente."
            )

        diferencia = (
            self.RENTA_MIN_LINEA_CREDITO
            - self.sueldo_mensual
        )

        diferencia_formateada = (
            self.formatear_pesos(
                diferencia
            )
        )

        return (
            "Tu Cuenta Corriente está activa, "
            "pero tu renta todavía no cumple "
            "el requisito para Línea de Crédito. "
            f"Faltan ${diferencia_formateada}."
        )

    # =====================================================
    # TARJETA DE CRÉDITO
    # =====================================================

    @property
    def puede_tarjeta_credito(self):

        return (
            self.sueldo_mensual
            >= self.RENTA_MIN_TARJETA_CREDITO
            and self.estado == "ACTIVA"
        )

    @property
    def estado_tarjeta_credito(self):

        if self.estado != "ACTIVA":

            return (
                "La cuenta debe estar activa."
            )

        if self.tarjeta_credito_solicitada:

            return (
                "Solicitud de Tarjeta de Crédito "
                "enviada y en proceso de evaluación."
            )

        if self.puede_tarjeta_credito:

            return (
                "Cumples los requisitos para "
                "solicitar una Tarjeta de Crédito."
            )

        diferencia = (
            self.RENTA_MIN_TARJETA_CREDITO
            - self.sueldo_mensual
        )

        diferencia_formateada = (
            self.formatear_pesos(
                diferencia
            )
        )

        return (
            "Renta insuficiente para solicitar "
            "una Tarjeta de Crédito. "
            f"Faltan ${diferencia_formateada}."
        )

    # =====================================================
    # REPRESENTACIÓN
    # =====================================================

    def __str__(self):

        return (
            f"{self.numero_cuenta} "
            f"- {self.titular}"
        )

    class Meta:

        verbose_name = (
            "Cuenta bancaria"
        )

        verbose_name_plural = (
            "Cuentas bancarias"
        )

        ordering = [
            "numero_cuenta"
        ]