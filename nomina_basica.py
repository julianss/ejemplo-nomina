"""nomina_basica.py
Cálculo simplificado de nómina mexicana 2025.

Entradas:
    - sueldo_diario (float): sueldo base diario del trabajador.
    - factor_integracion (float): factor de integración para IMSS (p. ej. 1.0452).
    - dias_trabajados (int): número de días que cubre el periodo de pago.

Salidas (dict):
    - percepciones:
        - sueldo: sueldo bruto del periodo
    - deducciones:
        - imss: cuota obrero IMSS del periodo
        - isr: retención de ISR del periodo
    - neto: sueldo neto a pagar

NOTA: Este script se basa en las tarifas oficiales de ISR e IMSS vigentes para 2025
publicadas en el DOF y por el IMSS.  Los cálculos son referenciales y NO sustituyen
una solución de nómina certificada.
"""


# ---- Parámetros y tablas 2025 ------------------------------------------------

UMA_2025 = 113.14  # Unidad de Medida y Actualización vigente en 2025 (pesos diarios)

# Tabla diaria ISR 2025: (lim_inf, lim_sup, cuota_fija, porc_excedente)
ISR_DIARIA = [
    (0.01,      24.54,     0.00,   1.92),
    (24.54,     208.29,    0.47,   6.40),
    (208.30,    366.05,   12.23,  10.88),
    (366.06,    425.52,   29.40,  16.00),
    (425.53,    509.46,   38.91,  17.92),
    (509.47,   1027.52,   53.95,  21.36),
    (1027.53,  1619.51,  164.61,  23.52),
    (1619.52,  3091.90,  303.85,  30.00),
    (3091.91,  4122.54,  745.56,  32.00),
    (4122.55, 12367.62, 1075.37,  34.00),
    (12367.63, float('inf'), 3878.69, 35.00),
]

# Subsidio al empleo diario 2025: (lim_inf, lim_sup, subsidio)
SUBSIDIO_DIARIO = [
    (0.01,    58.19, 13.39),
    (58.20,   87.28, 13.38),
    (87.29,  114.24, 13.38),
    (114.25, 116.38, 12.92),
    (116.39, 146.25, 12.58),
    (146.26, 155.17, 11.65),
    (155.18, 175.51, 10.69),
    (175.52, 204.76,  9.69),
    (204.77, 234.01,  8.34),
    (234.02, 242.84,  7.16),
    (242.85, float('inf'), 0.00),
]


# ---- Funciones auxiliares -----------------------------------------------------

def _buscar_rango(valor, tabla, campos):
    """Devuelve la tupla de la tabla cuyo rango contiene `valor`. Los campos
    es la lista de índices que se devolverán (por defecto toda la tupla)."""
    for fila in tabla:
        lim_inf, lim_sup, *resto = fila
        if lim_inf <= valor <= lim_sup:
            if campos is None:
                return fila
            return tuple(fila[i] for i in campos)
    raise ValueError(f"Valor {valor} fuera de rango de la tabla.")


def _calcular_isr_diario(sueldo_diario):
    lim_inf, lim_sup, cuota_fija, porc = _buscar_rango(
        sueldo_diario, ISR_DIARIA, None
    )
    excedente = sueldo_diario - lim_inf
    isr_pre_subsidio = cuota_fija + excedente * (porc / 100.0)

    # Subsidio al empleo
    _, _, subsidio = _buscar_rango(
        sueldo_diario, SUBSIDIO_DIARIO, None
    )

    isr_diario = max(isr_pre_subsidio - subsidio, 0.0)
    return isr_diario


def _calcular_imss_diario(sbc_diario):
    """Cuotas obrero vigentes 2025 (aprox.)"""
    # Enfermedades y maternidad (prestaciones en dinero)
    cuota_em_dinero = 0.0025 * sbc_diario

    # Cuota adicional sobre excedente de 3 UMA
    excedente_3uma = max(sbc_diario - 3 * UMA_2025, 0.0)
    cuota_em_excedente = 0.0040 * excedente_3uma

    # Gastos médicos pensionados y beneficiarios
    cuota_gmp = 0.00375 * sbc_diario

    # Invalidez y vida
    cuota_inv_vida = 0.00625 * sbc_diario

    # Cesantía en edad avanzada y vejez (trabajador)
    cuota_ceav = 0.01125 * sbc_diario

    return sum((
        cuota_em_dinero,
        cuota_em_excedente,
        cuota_gmp,
        cuota_inv_vida,
        cuota_ceav,
    ))


# ---- API pública --------------------------------------------------------------

def calcular_nomina(sueldo_diario: float,
                    factor_integracion: float,
                    dias_trabajados: int):
    """Devuelve un dict con percepciones, deducciones y neto."""
    if sueldo_diario <= 0 or factor_integracion <= 0 or dias_trabajados <= 0:
        raise ValueError("Todos los parámetros deben ser positivos.")

    # Percepción principal
    sueldo_periodo = sueldo_diario * dias_trabajados

    # Salario base de cotización diario
    sbc_diario = sueldo_diario * factor_integracion

    # Deducciones IMSS
    imss_diario = _calcular_imss_diario(sbc_diario)
    imss_periodo = imss_diario * dias_trabajados

    # ISR
    isr_diario = _calcular_isr_diario(sueldo_diario)
    isr_periodo = isr_diario * dias_trabajados

    percepciones = {
        "sueldo": round(sueldo_periodo, 2),
    }
    deducciones = {
        "imss": round(imss_periodo, 2),
        "isr": round(isr_periodo, 2),
    }
    neto = round(sueldo_periodo - imss_periodo - isr_periodo, 2)

    return {
        "percepciones": percepciones,
        "deducciones": deducciones,
        "neto": neto,
    }


# ---- Uso de ejemplo -----------------------------------------------------------
if __name__ == "__main__":
    # Ejemplo rápido
    datos = calcular_nomina(
        sueldo_diario=500,
        factor_integracion=1.0452,
        dias_trabajados=15,
    )
    import pprint
    pprint.pp(datos)
