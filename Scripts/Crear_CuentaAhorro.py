from playwright.sync_api import Page, expect
from datetime import datetime
from Scripts.helpers import fecha_inicio_SAP
import time

def navegar_a_crear_cuenta(page: Page, cliente, fecha_inicio: str):
    """
    Navega desde el Home de SAP hasta la pantalla de creación de cuentas.
    """
    print("Navegando a 'Deposit Accounts'...")
    
    # 1. Click en 'More groups'
    page.get_by_label("More groups").click()
    
    # 2. Seleccionar 'Deposit Accounts'
    deposit_menu = page.locator("[id=\"__item3-__list0-33-content\"]").get_by_text("Deposit Accounts")
    deposit_menu.wait_for(state="visible", timeout=10000)
    deposit_menu.click()
    
    # 3. Click en la transacción específica
    print("Abriendo 'Current Account Create/Change'...")
    page.get_by_role("link", name="Current Account Create/Change").click()
    
    # 4. Espera a que la nueva pantalla cargue
    page.wait_for_load_state("networkidle")

    # 5 Llenado del campo Cliente
    print(f"Ingresando cliente: {cliente}")
    page.get_by_role("textbox", name="Customer No").click()
    page.get_by_role("textbox", name="Customer No").fill(str(cliente))
    page.get_by_role("button", name="Search", exact=True).click()
    
    # 6. Seleccionando el resultado de la búsqueda
    page.get_by_text(str(cliente)).click()
    # IMPORTANTE: Esperar a que la página "reaccione" al clic del cliente
    page.wait_for_selector("text=Create", state="visible")
    page.wait_for_timeout(2500)
    
    # 7. Creando nueva cuenta de ahorro
    btn_create = page.get_by_role("button", name="Create", exact=True)
    btn_create.wait_for(state="attached")# Espera a que el botón sea 'enabled' (que SAP no lo esté bloqueando)
    time.sleep(6)
    btn_create.click()
    
    # 8. Llamando a la función para seleccionar la fecha de inicio
    fecha_inicio_SAP(page, fecha_inicio)

    # 9. Finalizar con el botón Continue
    # Este botón confirma la selección dentro del diálogo de SAP
    page.get_by_role("button", name="Continue", exact=True).click()

    #10. Haciendo click en la cuenta
    page.locator("div.sapMSLIDescription:has-text('Oficina Principal C4B')").click()
    #11. Haciendo click en la cuenta de ahorro
    page.wait_for_timeout(5000)
    selector_cuenta = "span[id$='-titleText-inner']"
    
    # 12. Seleccionando Cuenta de ahorro Aplicando filtro de texto para asegurar que sea la cuenta correcta
    # Usa .first para quedarnos solo con una
    cuenta_locator = page.locator(selector_cuenta).filter(has_text="Cuenta De Ahorro Pacific Bank").first
    cuenta_locator.scroll_into_view_if_needed()
    cuenta_locator.click(force=True)
    # 13. Llenando el campo de condición de grupo con la opción correcta
    input_field = page.locator("#__input60-inner")
    input_field.click()
    input_field.fill("TEST MARIO")
    
    # 14. Localizando el componente Select por su ID base
    select_box = page.locator("#__xmlview1--selectConditionGroup")
    select_box.click()
    page.wait_for_timeout(800) 
    
    # 15. Seleccionando el elemento por el texto que contiene
    # Usando el rol 'option' que SAP asigna a los elementos del menú desplegado
    opcion = page.get_by_role("option", name="CTA_AHO_REG-Savings Loc Natural")
    opcion.wait_for(state="visible")
    opcion.click()
    page.get_by_role("button", name="Save").click()
    page.wait_for_timeout(2000)
    page.get_by_role("button", name="OK", exact=True).click()
    page.wait_for_timeout(5000)

    # Buscamos el elemento y esperamos hasta que su texto no esté vacío
    locator_numero = page.locator("#application-ZBAOAMCACCRU_O-display-component---detail--objectHeader-titleText-inner")

    # Esperamos a que el texto cambie de estar vacío a tener contenido
    page.wait_for_function(
    "selector => document.querySelector(selector).innerText.trim().length > 0", 
    arg="#application-ZBAOAMCACCRU_O-display-component---detail--objectHeader-titleText-inner"
)

    numero_operacion = locator_numero.inner_text().strip()
    print(f"Número de operación creado: {numero_operacion}")
    return numero_operacion