"""Datos simulados y constantes de navegación para el tablero."""

DATE_RANGES = ["Últimos 7 días", "Últimos 30 días", "Últimos 90 días"]
DEFAULT_RANGE = "Últimos 30 días"
ZONA_LOCATIONS = ["VDM", "Centro", "Occidente"]
CEDIS_BY_ZONA = {
    "VDM": [
        "Atizapan",
        "Chalco",
        "Ecatepec",
        "Mixcoac",
        "Naucalpan",
        "Reyes",
        "Tecamac",
        "Texcoco",
        "Tlahuac",
        "Tultitlan",
        "Valle Norte",
        "Valle Sur",
    ],
    "Centro": [
        "Cuautla",
        "Huejutla",
        "Jiutepec",
        "Pachuca",
        "Puebla 1",
        "Puebla 2",
        "Queretaro",
        "San Juan del Rio",
        "Tehuacan",
        "Tlaxcala",
        "Toluca",
        "Tula",
    ],
    "Occidente": [
        "Aguascalientes",
        "Ameca",
        "Apatzingan",
        "Autlan",
        "Cd. Guzman",
        "Celaya",
        "Colima",
        "Dolores",
        "Fresnillo",
        "Irapuato",
        "Jerez",
        "La Piedad",
        "Lazaro Cardenas",
        "Leon",
        "Manzanillo",
        "Morelia",
        "Puerto Vallarta",
        "Rio Grande",
        "Tepatitlan",
        "Tlajomulco",
        "Tlaquepaque",
        "Uringato",
        "Uruapan",
        "Zacatecas",
        "Zamora",
        "Zapopan",
    ],
}
CEDIS_LOCATIONS = [
    cedis for zona in ZONA_LOCATIONS for cedis in CEDIS_BY_ZONA[zona]
]
DEFAULT_ZONA = ZONA_LOCATIONS[0]
DEFAULT_CEDIS = CEDIS_BY_ZONA[DEFAULT_ZONA][0]
ZONA_BY_CEDIS = {
    cedis: zona
    for zona, cedis_list in CEDIS_BY_ZONA.items()
    for cedis in cedis_list
}
NAV_ITEMS = [
    {
        "label": "Tablero",
        "icon": "layout-dashboard",
        "href": "/",
        "key": "dashboard",
    },
    {
        "label": "Regiones",
        "icon": "building-2",
        "href": "/regiones",
        "key": "regiones",
    },
    {
        "label": "Tareas",
        "icon": "file-text",
        "href": "/tareas",
        "key": "tareas",
    },
    {
        "label": "Historial",
        "icon": "history",
        "href": "/historial",
        "key": "historial",
    },
    {
        "label": "Acerca",
        "icon": "info",
        "href": "/acerca",
        "key": "about",
    },
]

CEDIS_DETAILS_BY_ZONA = {
    "VDM": {
        "status": "Vigente",
        "autoridad": "SEMADET",
        "permiso_medio_ambiente_municipal": True,
        "permiso_descarga_municipal": False,
        "equipo_siga": "S. Martinez",
        "permits": "9",
        "capacity": "25,600 m2",
    },
    "Centro": {
        "status": "En revision",
        "autoridad": "SIAPA",
        "permiso_medio_ambiente_municipal": True,
        "permiso_descarga_municipal": True,
        "equipo_siga": "L. Orozco",
        "permits": "7",
        "capacity": "21,300 m2",
    },
    "Occidente": {
        "status": "Vigente",
        "autoridad": "Medio Ambiente y Desarrollo Territorial",
        "permiso_medio_ambiente_municipal": False,
        "permiso_descarga_municipal": True,
        "equipo_siga": "A. Ruiz",
        "permits": "5",
        "capacity": "16,900 m2",
    },
}

CEDIS_DETAILS = {
    cedis: {"name": "CEDIS", **CEDIS_DETAILS_BY_ZONA[zona]}
    for zona, cedis_list in CEDIS_BY_ZONA.items()
    for cedis in cedis_list
}

PERMITS_BY_ZONA = {
    "VDM": [
        {
            "nombre": "Operacion sanitaria",
            "asunto": "",
            "registro": "",
            "gobierno": "Federal",
            "numero": "VDM-5582",
            "fecha_emision": "2022-06-08",
            "vigencia": "2025-08-15",
            "cedis": "VDM",
            "pdfs": [],
            "status": "Vigente",
        },
        {
            "nombre": "Transporte refrigerado",
            "asunto": "",
            "registro": "",
            "gobierno": "Estatal",
            "numero": "VDM-2044",
            "fecha_emision": "2023-01-26",
            "vigencia": "2026-01-04",
            "cedis": "VDM",
            "pdfs": [],
            "status": "Vigente",
        },
        {
            "nombre": "Seguridad industrial",
            "asunto": "",
            "registro": "",
            "gobierno": "Municipal",
            "numero": "VDM-3377",
            "fecha_emision": "2022-03-19",
            "vigencia": "2024-11-22",
            "cedis": "VDM",
            "pdfs": [],
            "status": "Por vencer",
        },
    ],
    "Centro": [
        {
            "nombre": "Operacion sanitaria",
            "asunto": "",
            "registro": "",
            "gobierno": "Federal",
            "numero": "CTR-1201",
            "fecha_emision": "2021-08-11",
            "vigencia": "2025-05-30",
            "cedis": "Centro",
            "pdfs": [],
            "status": "Vigente",
        },
        {
            "nombre": "Almacen central",
            "asunto": "",
            "registro": "",
            "gobierno": "Estatal",
            "numero": "CTR-4429",
            "fecha_emision": "2023-04-03",
            "vigencia": "2026-03-18",
            "cedis": "Centro",
            "pdfs": [],
            "status": "Vigente",
        },
        {
            "nombre": "Seguridad industrial",
            "asunto": "",
            "registro": "",
            "gobierno": "Municipal",
            "numero": "CTR-3008",
            "fecha_emision": "2022-10-29",
            "vigencia": "2024-10-05",
            "cedis": "Centro",
            "pdfs": [],
            "status": "Por vencer",
        },
    ],
    "Occidente": [
        {
            "nombre": "Operacion sanitaria",
            "asunto": "",
            "registro": "",
            "gobierno": "Federal",
            "numero": "OCC-3302",
            "fecha_emision": "2022-11-09",
            "vigencia": "2025-07-12",
            "cedis": "Occidente",
            "pdfs": [],
            "status": "Vigente",
        },
        {
            "nombre": "Transporte terrestre",
            "asunto": "",
            "registro": "",
            "gobierno": "Estatal",
            "numero": "OCC-1843",
            "fecha_emision": "2023-02-17",
            "vigencia": "2026-04-09",
            "cedis": "Occidente",
            "pdfs": [],
            "status": "Vigente",
        },
        {
            "nombre": "Seguridad industrial",
            "asunto": "",
            "registro": "",
            "gobierno": "Municipal",
            "numero": "OCC-2901",
            "fecha_emision": "2021-06-22",
            "vigencia": "2024-09-27",
            "cedis": "Occidente",
            "pdfs": [],
            "status": "Por vencer",
        },
    ],
}


def _permits_for_cedis(cedis: str, permits: list[dict]) -> list[dict]:
    updated: list[dict] = []
    for permit in permits:
        entry = dict(permit)
        entry["cedis"] = cedis
        updated.append(entry)
    return updated


PERMITS_BY_CEDIS = {
    cedis: _permits_for_cedis(cedis, PERMITS_BY_ZONA[zona])
    for zona, cedis_list in CEDIS_BY_ZONA.items()
    for cedis in cedis_list
}

DEFAULT_PERMIT = PERMITS_BY_CEDIS[DEFAULT_CEDIS][0]

PERMIT_MIX = [
    {"name": "Sanitario", "value": 45},
    {"name": "Logistica", "value": 32},
    {"name": "Seguridad", "value": 23},
]

DATASETS = {
    "Últimos 7 días": {
        "kpis": {
            "sales": {
                "title": "Ventas totales",
                "value": "$42,340",
                "delta": "+12.4%",
                "trend": "up",
            },
            "visitors": {
                "title": "Visitantes totales",
                "value": "98,210",
                "delta": "+4.2%",
                "trend": "up",
            },
            "repeat": {
                "title": "Cliente recurrente",
                "value": "28.3%",
                "delta": "-2.1%",
                "trend": "down",
            },
        },
        "sales_over_time": [
            {"day": "Lun", "sales": 4200},
            {"day": "Mar", "sales": 5200},
            {"day": "Mie", "sales": 4800},
            {"day": "Jue", "sales": 6100},
            {"day": "Vie", "sales": 7000},
            {"day": "Sab", "sales": 6400},
            {"day": "Dom", "sales": 7200},
        ],
        "visitors_over_time": [
            {"day": "Lun", "visitors": 10200},
            {"day": "Mar", "visitors": 9800},
            {"day": "Mie", "visitors": 11200},
            {"day": "Jue", "visitors": 12400},
            {"day": "Vie", "visitors": 13100},
            {"day": "Sab", "visitors": 11800},
            {"day": "Dom", "visitors": 14000},
        ],
        "customers_over_time": [
            {"day": "Lun", "new": 340, "repeat": 160},
            {"day": "Mar", "new": 360, "repeat": 150},
            {"day": "Mie", "new": 320, "repeat": 170},
            {"day": "Jue", "new": 390, "repeat": 190},
            {"day": "Vie", "new": 420, "repeat": 180},
            {"day": "Sab", "new": 380, "repeat": 175},
            {"day": "Dom", "new": 440, "repeat": 195},
        ],
        "history": [
            {"month": "Enero", "value": 18200, "target": 22000, "percent": 83},
            {"month": "Febrero", "value": 20100, "target": 24000, "percent": 84},
            {"month": "Marzo", "value": 23600, "target": 26000, "percent": 90},
            {"month": "Abril", "value": 21400, "target": 25000, "percent": 86},
        ],
    },
    "Últimos 30 días": {
        "kpis": {
            "sales": {
                "title": "Ventas totales",
                "value": "$186,420",
                "delta": "+8.1%",
                "trend": "up",
            },
            "visitors": {
                "title": "Visitantes totales",
                "value": "420,540",
                "delta": "+5.8%",
                "trend": "up",
            },
            "repeat": {
                "title": "Cliente recurrente",
                "value": "31.7%",
                "delta": "+1.2%",
                "trend": "up",
            },
        },
        "sales_over_time": [
            {"day": "Semana 1", "sales": 42000},
            {"day": "Semana 2", "sales": 51200},
            {"day": "Semana 3", "sales": 46800},
            {"day": "Semana 4", "sales": 56420},
        ],
        "visitors_over_time": [
            {"day": "Semana 1", "visitors": 98000},
            {"day": "Semana 2", "visitors": 104500},
            {"day": "Semana 3", "visitors": 101200},
            {"day": "Semana 4", "visitors": 116840},
        ],
        "customers_over_time": [
            {"day": "Semana 1", "new": 1880, "repeat": 720},
            {"day": "Semana 2", "new": 2010, "repeat": 820},
            {"day": "Semana 3", "new": 1930, "repeat": 790},
            {"day": "Semana 4", "new": 2240, "repeat": 860},
        ],
        "history": [
            {"month": "Enero", "value": 58200, "target": 65000, "percent": 89},
            {"month": "Febrero", "value": 61400, "target": 69000, "percent": 89},
            {"month": "Marzo", "value": 70220, "target": 76000, "percent": 92},
            {"month": "Abril", "value": 64800, "target": 72000, "percent": 90},
        ],
    },
    "Últimos 90 días": {
        "kpis": {
            "sales": {
                "title": "Ventas totales",
                "value": "$548,320",
                "delta": "+6.6%",
                "trend": "up",
            },
            "visitors": {
                "title": "Visitantes totales",
                "value": "1.2M",
                "delta": "+3.4%",
                "trend": "up",
            },
            "repeat": {
                "title": "Cliente recurrente",
                "value": "29.1%",
                "delta": "-0.8%",
                "trend": "down",
            },
        },
        "sales_over_time": [
            {"day": "Ene", "sales": 168000},
            {"day": "Feb", "sales": 182400},
            {"day": "Mar", "sales": 197600},
            {"day": "Abr", "sales": 200320},
        ],
        "visitors_over_time": [
            {"day": "Ene", "visitors": 380000},
            {"day": "Feb", "visitors": 404000},
            {"day": "Mar", "visitors": 418000},
            {"day": "Abr", "visitors": 455000},
        ],
        "customers_over_time": [
            {"day": "Ene", "new": 8200, "repeat": 3200},
            {"day": "Feb", "new": 8800, "repeat": 3400},
            {"day": "Mar", "new": 9100, "repeat": 3600},
            {"day": "Abr", "new": 9600, "repeat": 3700},
        ],
        "history": [
            {"month": "Enero", "value": 168000, "target": 190000, "percent": 88},
            {"month": "Febrero", "value": 182400, "target": 200000, "percent": 91},
            {"month": "Marzo", "value": 197600, "target": 215000, "percent": 92},
            {"month": "Abril", "value": 200320, "target": 220000, "percent": 91},
        ],
    },
}

DEFAULT_DATA = DATASETS[DEFAULT_RANGE]
