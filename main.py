from playwright.sync_api import sync_playwright
from Scripts.config_loader import cargar_configuracion
from Scripts.helpers import login_sap
from Scripts.Crear_CuentaAhorro import navegar_a_crear_cuenta
from Scripts.Creacion_Contrato import crear_contrato
import sys

def ejecutar_poc():
    # 1. Cargar los datos desde el archivo Config.xlsx
    print("---PASO 1: Cargando datos del Excel---")
    config = cargar_configuracion()
    
    if config is None:
        print("Error crítico: No se pudo leer el archivo de configuración.")
        sys.exit(1)

    # 2. Iniciar el motor de Playwright
    # EL "with" ES INDISPENSABLE para que la variable 'p' funcione
    with sync_playwright() as p:
        print("---PASO 2: Iniciando Playwright con bypass de seguridad---")
        
        # Lanzamos el navegador con el argumento para ignorar errores de certificado a nivel motor
        browser = p.chromium.launch(
            headless=False, 
            slow_mo=500,
            args=["--ignore-certificate-errors"]
        )
        
        # Creamos el contexto ignorando errores HTTPS a nivel protocolo
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            ignore_https_errors=True,
            http_credentials={
                "username": config['usuario'], 
                "password": config['password']
            }
        )
        
        page = context.new_page()

        try:
            # 3. Llamar a la función de Login inteligente
            print(f"---PASO 3: Iniciando sesión en {config.get('ambiente', 'SAP')}---")
            
            login_sap(
                page, 
                url=config['url'], 
                user=config['usuario'], 
                password=config['password']
            )
            #Formateando Fecha
            fecha_formateada = config['fecha_inicio'].strftime("%d/%m/%Y")
            num_cuenta_creada = navegar_a_crear_cuenta(page, str(config['cliente']), fecha_formateada)
            crear_contrato(page, str(config['cliente']), fecha_formateada, num_cuenta_creada)
            #navegar_a_crear_cuenta(page, str(config['cliente']), fecha_formateada)
            #crear_contrato(page, str(config['cliente']), fecha_formateada)
            

            # 4. Mantener la sesión abierta para validar el resultado
            print("---PROCESO FINALIZADO---")
            print("Presiona Enter en esta terminal para cerrar el navegador...")
            input()

        except KeyError as e:
            print(f"Error: No se encontró la columna {e} en el archivo Excel.")
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
        finally:
            # Cerramos todo de forma limpia
            context.close()
            browser.close()

if __name__ == "__main__":
    ejecutar_poc()