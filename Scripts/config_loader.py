import pandas as pd
import os
#Script para cargar la configuración desde un archivo Excel
def cargar_configuracion(nombre_hoja='Hoja1'):
    """
    Lee los datos del archivo Excel ubicado en la carpeta Configuracion.
    """
    # Ruta dinámica para que funcione en cualquier PC
    ruta_base = os.path.dirname(os.path.dirname(__file__))
    ruta_excel = os.path.join(ruta_base, 'Configuracion', 'Config.xlsx')

    try:
        #Leer Excel
        df = pd.read_excel(ruta_excel, sheet_name=nombre_hoja)
        #Convertir a diccionario
        config_dict = df.iloc[0].to_dict()
        return config_dict
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_excel}")
        return None
    except Exception as e:
        print(f"Error al leer Excel: {e}")
        return None
    