from playwright.sync_api import Page
from datetime import datetime

def login_sap(page: Page, url, user, password):
    """
    Realiza el login en SAP manejando pop-ups automáticos del navegador.
    """
    
    # --- 1. CONFIGURAR EL MANEJO DE POP-UPS (DIALOGS) ---
    # Esta línea es "mágica": le dice a Playwright que en cuanto aparezca 
    # cualquier alerta o confirmación, le dé a "Aceptar" inmediatamente.
    page.on("dialog", lambda dialog: dialog.accept())

    print(f"Navegando a: {url}")
    
    # --- 2. NAVEGACIÓN ---
    # Usamos wait_until="commit" para que nos dé el control en cuanto el 
    # servidor responda, permitiendo que el manejador de dialogs actúe rápido.
    page.goto(url, wait_until="commit")

    try:
        # --- 3. LLENADO DE FORMULARIO ---
        # Esperamos inteligentemente a que el cuadro de 'User' sea visible
        input_user = page.get_by_role('textbox', name='User')
        input_user.wait_for(state="visible", timeout=10000)
        
        print("Insertando credenciales de SAP...")
        input_user.fill(str(user))
        page.get_by_role('textbox', name='Password').fill(str(password))
        
        # Clic en Log On
        page.get_by_role('button', name='Log On').click()
        
        # Esperamos a que cargue la página interna de SAP
        page.wait_for_load_state("networkidle")
        print("Login completado.")

    except Exception as e:
        print(f"Nota: No se pudo interactuar con el formulario. Error: {e}")
        # A veces, tras el pop-up, ya estamos dentro. Verificamos si existe el header de SAP.
        if page.locator("#shell-header").is_visible():
            print("Ya estabas dentro de SAP (posible Single Sign-On).")
        else:
            print("No se encontró el formulario ni el inicio de SAP.")

def fecha_inicio_SAP(page, fecha_inicio):
    """
    Función para seleccionar la fecha de inicio en el date picker de SAP
    """
    fecha_obj = datetime.strptime(fecha_inicio, "%d/%m/%Y")#Conviertiendo la fecha de String a Date object
    anio = int(fecha_obj.year) #Extrayendo el año
    nombre_mes = fecha_obj.strftime("%B") #Usando el nombre del mes, formato utilizado por SAP
    dia = fecha_obj.day #Extrayendo el día

    #Abrir vista de navegación referente al año
    page.locator("#CACStartDateCalendar--Head-B2").click()
    print("Date picker abierto")
    """
    Iniciando un bucle para buscar la fecha deseada en la vista del date picker
    si esta no se encuentra, recorrera hacia atrás o adelante según la lógica programada
    """
    while True:
        #Buscando el anó en la vista actual
        selector_anio = f"div[data-sap-year-start^='{anio}']"
        if page.locator(selector_anio).count() > 0:
            page.locator(selector_anio).first.click()
            break
        #Obtención y formato del año en curso
        anio_texto = page.locator("#CACStartDateCalendar--Head-B2").inner_text().strip()
        anio_actual = int(anio_texto[:4]) #Se toman unicamente los últimos cuatro digitos
        #Comparación entre año recibido y el año actual para determinar la dirección de navegación
        if anio < anio_actual:
            page.locator("#CACStartDateCalendar--Head-prev").click()
        else:
            page.locator("#CACStartDateCalendar--Head-next").click()
            page.wait_for_timeout(500)
            print(f"Año {anio} seleccionado correctamente")
    #Seleccionando el mes
    page.locator("#CACStartDateCalendar--Head-B1").click()
    selector_mes = f"div[role='gridcell'][aria-label='{nombre_mes} {anio}']"
    mes_locator = page.locator(selector_mes)
    mes_locator.wait_for(state="visible")
    mes_locator.click()
    print(f"Mes {nombre_mes} seleccionado correctamente")
    #Seleccionando el día
    fecha_sap = fecha_obj.strftime("%Y%m%d")
    selector_dia = f"div[data-sap-day='{fecha_sap}']"
    dia_locator = page.locator(selector_dia)
    dia_locator.wait_for(state="visible")
    dia_locator.click()
    print(f"Fecha {fecha_inicio} seleccionada correctamente")