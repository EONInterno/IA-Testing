# Automatización SAP - EONInterno

Este proyecto contiene los scripts de automatización para procesos críticos en SAP, utilizando Python y Playwright.

## Estructura del Proyecto
- `main.py`: Punto de entrada principal.
- `Scripts/`: Módulos de lógica de negocio y automatización.
    - `Crear_CuentaAhorro.py`: Automatización de creación de cuentas.
    - `Creacion_Contrato.py`: Automatización de contratos.
    - `helpers.py`: Funciones de utilidad y lógica compartida.
    - `config_loader.py`: Gestión de configuración y datos.

## Prerrequisitos
- Python 3.9+
- Playwright instalado (`pip install playwright` y `playwright install`)
- VPN corporativa activa para acceso a SAP.

## Instalación
```bash
# Clonar el repo
git clone [https://github.com/EONInterno/IA-Testing.git](https://github.com/EONInterno/IA-Testing.git)
cd IA-Testing

# Instalar dependencias
pip install -r requirements.txt
playwright install