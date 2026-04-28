# Fase 1 — Conexión VPN y Login SAP Fiori

## Descripción

Scripts de automatización para:
1. Conectar a la VPN corporativa (Cisco AnyConnect / openconnect)
2. Realizar login en SAP Fiori Launchpad

## Estructura

```
fase1/
├── main.py                # Orquestador principal
├── vpn_connect.py         # Conexión VPN
├── sap_login.py           # Login SAP Fiori con Playwright
├── requirements.txt       # Dependencias Python
├── README.md              # Este archivo
└── evidencia/
    ├── screenshots/       # Capturas de pantalla
    │   ├── 01_vpn_connected.png
    │   ├── 02_sap_login_page.png
    │   ├── 03_sap_credentials_entered.png
    │   └── 04_sap_home_loaded.png
    ├── videos/            # Videos de la sesión Playwright
    └── reporte_fase1.txt  # Reporte de ejecución
```

## Prerrequisitos

- Python 3.9+
- Acceso a VPN corporativa (Cisco AnyConnect u openconnect)
- Credenciales VPN y SAP

## Instalación

```bash
pip install -r fase1/requirements.txt
python -m playwright install chromium
```

## Variables de Entorno

Configurar antes de ejecutar:

| Variable       | Descripción                     |
|---------------|---------------------------------|
| `VPN_HOST`    | Host/IP del servidor VPN        |
| `VPN_USER`    | Usuario VPN                     |
| `VPN_PASSWORD`| Contraseña VPN                  |
| `SAP_USER`    | Usuario SAP Fiori               |
| `SAP_PASSWORD`| Contraseña SAP Fiori            |

## Ejecución

```bash
export VPN_HOST='...'
export VPN_USER='...'
export VPN_PASSWORD='...'
export SAP_USER='...'
export SAP_PASSWORD='...'

python fase1/main.py
```

## Evidencia

Tras la ejecución se genera:
- Screenshots de cada paso en `evidencia/screenshots/`
- Video de la sesión Playwright en `evidencia/videos/`
- Reporte con timestamps y estados en `evidencia/reporte_fase1.txt`

## Notas

- Los archivos de evidencia NO se deben commitear al repositorio.
- Las credenciales NUNCA deben estar hardcodeadas en el código.
- Si Cisco AnyConnect no está disponible, se usa `openconnect` como alternativa.
- SAP usa certificados autofirmados; se usa `ignore_https_errors=True`.
