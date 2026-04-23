from playwright.sync_api import Page, expect
from datetime import datetime
import time
from Scripts.helpers import fecha_inicio_SAP
import re
    
def crear_contrato(page: Page, cliente, fecha_inicio, numero_cuenta: str):
    """
    Navega desde el Home de SAP hasta la pantalla de creación de contratos.
    """
    print("Navegando a sección Loan Contract...")
    page.locator("#shell-header-icon").click(force=True)
    time.sleep(6)
    # 1. Click en 'More groups'
    page.get_by_label("More groups").click()
    # 2. Seleccionar 'Loan Accounts'
    loan_menu_item = page.get_by_role("listitem").filter(has_text="Loan Accounts")
    #selector_loanAccounts =page.locator('[id="__item3-__list0-38-content"]').get_by_text('Loan Accounts')
    loan_menu_item.wait_for(state="visible", timeout=10000)
    loan_menu_item.click()
    # 3. Click en la transacción específica
    page.get_by_role('link', name='Loan Contract Create Tile').click()
    print(f"Buscando cliente: {cliente}")
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
    btn_create.click()
    # 8. Llamando a la función para seleccionar la fecha de inicio
    fecha_inicio_SAP(page, fecha_inicio)
    # 9. Finalizar con el botón Continue
    # Este botón confirma la selección dentro del diálogo de SAP
    page.get_by_role("button", name="Continue", exact=True).click()
     #10. Haciendo click en la cuenta
    page.locator("div.sapMSLIDescription:has-text('Oficina Principal C4B')").click()
    cuenta_locator = page.locator("span.sapMTextLineClamp").filter(has_text="Personal Loan C4B").first
    cuenta_locator.scroll_into_view_if_needed()
    cuenta_locator.click(force=True)
    #---SECCIÓN 1: CONTRACT---
    # 11. Monto del contrato
    page.locator("input[name='LoanAmount']").fill("10000.00")
    # 12. Duración de contrato
    page.locator("input[id$='DurationNumber-inner']").fill("3") #Escribiendo duración del contrato
    page.locator("[id$='--DurationType-arrow']").click() #Abriendo picklist
    opcion_meses = page.locator("li[role='option']").filter(has_text="Months").first #Eligiendo unidad de medida de duración
    opcion_meses.wait_for(state="visible", timeout=5000)
    opcion_meses.click()
    # 13. Eligiendo Fixing type
    page.locator("[id$='--idFixingType-arrow']").click()
    opcion_fixed = page.locator("li[role='option']").filter(has_text="Fixed Interest").first
    opcion_fixed.wait_for(state="visible", timeout=5000)
    opcion_fixed.click()
    page.get_by_role("button", name="NEXT").nth(0).click() #Continuar a la siguiente sección

    #---SECCIÓN 2: SETTLEMENT---
    # 14. Eligiendo Frecuencia
    page.locator("[id$='--idFrequency-arrow']").click()
    opcion_frecuencia = page.locator("li[role='option']").filter(has_text="Monthly").first
    opcion_frecuencia.click()
    # 15. Eligiendo la fecha clave (Key Date)
    page.locator("[id$='--idKeyDateType-arrow']").click()
    opcion_fecha = page.locator("li[role='option']").filter(has_text="Anniversary Date").first
    opcion_fecha.click()
    page.get_by_role("button", name="NEXT").nth(1).click() #Continuar a la siguiente sección

    #---SECCIÓN 3: CONDITIONS---
    page.fill("input[id*='idNominalInterest-inner']", "7")
    page.get_by_role("button", name="NEXT").nth(2).click()
    #---SECCIÓN 4: PARTIES ROLES---
    page.get_by_role("button", name="NEXT").nth(3).click()
    #De momento no se harán acciones en esta sección
    #---SECCIÓN 5: ADITIONAL LOANS CONDITIONS---
    # Sales Product
    page.locator("[id$='--idSalesProduct-arrow']").click()
    page.locator("li[role='option']").filter(has_text="Local CDP Consumer Loan").first.click()
    # Incoming
    page.locator("[id$='--idSector-arrow']").click()
    page.locator("li[role='option']").filter(has_text="Personal Loan").first.click()
    # FECI
    page.locator("[id$='--idIndicatorFECI-arrow']").click()
    page.locator("li[role='option']").filter(has_text="Interests Discount").first.click()
    # Preferential Indicator
    page.locator("[id$='--idIndicatorPreferential-arrow']").click()
    page.locator("li[role='option']").filter(has_text="Preferential").first.click()
    #Loan Clasification
    page.locator("[id$='--idLoanClassif-arrow']").click()
    page.locator("li[role='option']").filter(has_text="Mención Especial").first.click()
    #CINU Activitie
    page.locator("[id$='--IdCINUActivity-arrow']").click()
    page.locator("li[role='option']").filter(has_text="Préstamo Personal").first.click()
    page.get_by_role("button", name="NEXT").nth(4).click()
    #---SECCIÓN 6: PAYMENT PARTY---
    page.locator("[id$='--idRegionCode-arrow']").click()
    page.locator("li[role='option']").filter(has_text="PANAMA").first.click()

    page.locator("[id$='--idDDAccSelection-arrow']").click()
    numero_cuenta = numero_cuenta
    page.locator("li[role='option']").filter(has_text=re.compile(f"^{numero_cuenta}")).first.click()

    page.get_by_role("button", name="Calculate").click()
    time.sleep(6)
    # 3. Hacer clic en "CREATE LOAN"
    page.get_by_role("button", name="CREATE LOAN").click()
    # 4. Pausa de 6 segundos
    time.sleep(6)
    # 5. Extraer el texto del contrato
    # Usamos el ID específico que me diste para mayor precisión
    elemento_contrato = page.locator("#application-ZBAOLBLACCRT_O-display-component---detail--LoanContractID-text")
    loan_contract_id = elemento_contrato.inner_text()
    print(f"El ID del contrato extraído es: {loan_contract_id}")