"""
Fase 3 — Creación de Contrato de Préstamo en SAP Fiori
Conecta al Chrome del escritorio vía CDP, navega desde Shell Home hasta
la pantalla de Loan Contract Create, llena el formulario en 6 secciones
y captura el ID del contrato creado.

Los parámetros se solicitan por consola (dinámicos, no hardcodeados).
"""

import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

SAP_URL = (
    "https://10.165.6.8:44300/sap/bc/ui2/flp"
    "?sap-client=110&sap-language=EN#Shell-home"
)
CDP_ENDPOINT = "http://localhost:29229"
SCREENSHOTS_DIR = Path(__file__).parent / "evidencia" / "screenshots"

ENGLISH_MONTHS = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def screenshot(page, name: str):
    """Captura screenshot con nombre descriptivo."""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOTS_DIR / f"{name}.png"
    try:
        page.screenshot(path=str(path))
        print(f"  [Screenshot] {path.name}")
    except Exception:
        print(f"  [Screenshot] No se pudo capturar {path.name}")


def solicitar_parametros() -> dict:
    """Solicita todos los parámetros dinámicos por consola."""
    print("=" * 60)
    print("  FASE 3 — Creación de Contrato de Préstamo")
    print("=" * 60)
    print("\nIngrese los siguientes parámetros:\n")

    campos = {
        "id_cliente": "ID_CLIENTE (número de cliente)",
        "fecha_inicio": "FECHA_INICIO (dd/mm/yyyy)",
        "producto": "PRODUCTO (ej: Personal Loan C4B)",
        "monto": "MONTO del préstamo (ej: 10000)",
        "duracion": "DURACION (número)",
        "duracion_unidad": "DURACION_UNIDAD (Years / Months / Days)",
        "fixing_type": "FIXING_TYPE (ej: Fixed Interest)",
        "frecuencia": "FRECUENCIA de pago (ej: Weekly)",
        "key_date": "KEY_DATE (ej: Anniversary Date)",
        "tasa_interes": "TASA_INTERES nominal (ej: 7)",
        "sales_product": "SALES_PRODUCT (ej: Local CDP Consumer Loan)",
        "income": "INCOME (ej: Personal Loan)",
        "feci_indicator": "FECI_INDICATOR (ej: Interests Discount)",
        "preferential_indicator": "PREFERENTIAL_INDICATOR (ej: Preferential)",
        "loan_classification": "LOAN_CLASSIFICATION (ej: Mención Especial)",
        "cinu_activity_type": "CINU_ACTIVITY_TYPE (ej: Préstamo Personal)",
        "region_code": "REGION_CODE (ej: PANAMA)",
        "cuenta_debito": "CUENTA_DEBITO (cuenta para débito/desembolso)",
    }

    params = {}
    for key, label in campos.items():
        valor = input(f"  {label}: ").strip()
        params[key] = valor

    # Validaciones obligatorias
    obligatorios = [
        "id_cliente", "fecha_inicio", "producto", "monto",
        "duracion", "duracion_unidad", "frecuencia", "key_date",
        "tasa_interes", "sales_product", "income", "feci_indicator",
        "preferential_indicator", "loan_classification",
        "cinu_activity_type", "region_code", "cuenta_debito",
    ]
    faltantes = [k for k in obligatorios if not params.get(k)]
    if faltantes:
        print(f"\n[ERROR] Campos obligatorios faltantes: {', '.join(faltantes)}")
        sys.exit(1)

    # Validar fecha
    try:
        datetime.strptime(params["fecha_inicio"], "%d/%m/%Y")
    except ValueError:
        print("\n[ERROR] Formato de fecha inválido. Use dd/mm/yyyy")
        sys.exit(1)

    # Validar monto numérico
    try:
        float(params["monto"])
    except ValueError:
        print("\n[ERROR] El monto debe ser numérico.")
        sys.exit(1)

    # Validar duración numérica
    try:
        int(params["duracion"])
    except ValueError:
        print("\n[ERROR] La duración debe ser un número entero.")
        sys.exit(1)

    # Validar unidad de duración
    unidades_validas = {"years", "months", "days"}
    if params["duracion_unidad"].lower() not in unidades_validas:
        print(f"\n[ERROR] Unidad de duración inválida. Use: {', '.join(unidades_validas)}")
        sys.exit(1)

    print("\n  Parámetros recibidos:")
    for key, valor in params.items():
        print(f"    {key:30s}: {valor}")
    print()
    return params


# ---------------------------------------------------------------------------
# Navegación por date picker de SAP
# ---------------------------------------------------------------------------

def seleccionar_fecha_contrato(page, fecha_str: str):
    """Navega el date picker de SAP para seleccionar la fecha indicada."""
    fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
    anio_objetivo = fecha_obj.year
    mes_objetivo = fecha_obj.month
    dia_sap = fecha_obj.strftime("%Y%m%d")

    print(f"  [Fecha] Seleccionando {fecha_str}...")

    # Abrir picker de año
    year_btn = page.locator("button[id*='Head-B2']").first
    year_btn.click()
    page.wait_for_timeout(500)

    # Navegar al año correcto
    max_clicks = 30
    for _ in range(max_clicks):
        year_cell = page.locator(f"div[data-sap-year-start^='{anio_objetivo}']")
        if year_cell.count() > 0:
            year_cell.first.click()
            print(f"  [Fecha] Año {anio_objetivo} seleccionado")
            break
        header_text = year_btn.inner_text().strip()
        primer_anio = int(header_text.split()[0]) if header_text[0].isdigit() else 2026
        if anio_objetivo < primer_anio:
            page.locator("button[id*='Head-prev']").first.click()
        else:
            page.locator("button[id*='Head-next']").first.click()
        page.wait_for_timeout(300)
    else:
        raise Exception(
            f"No se encontró el año {anio_objetivo} después de {max_clicks} intentos."
        )

    page.wait_for_timeout(500)

    # Navegar al mes correcto usando las flechas del calendario
    month_name = ENGLISH_MONTHS[mes_objetivo]
    for _ in range(24):
        month_header = page.locator("button[id*='Head-B1']").first
        current_month_text = month_header.inner_text().strip()
        if month_name in current_month_text:
            break
        # Determinar dirección
        page.locator("button[id*='Head-next']").first.click()
        page.wait_for_timeout(300)
    else:
        raise Exception(
            f"No se encontró el mes {month_name} después de 24 intentos."
        )
    print(f"  [Fecha] Mes {month_name} visible")

    # Seleccionar el día
    day_cell = page.locator(f"div[data-sap-day='{dia_sap}']")
    day_cell.wait_for(state="visible", timeout=5000)
    day_cell.click()
    print(f"  [Fecha] Fecha {fecha_str} seleccionada correctamente")


# ---------------------------------------------------------------------------
# Sección 1: Contract
# ---------------------------------------------------------------------------

def llenar_seccion_contract(page, params: dict):
    """Llena los campos de la sección 1. Contract."""
    print("\n[Sección 1] Contract")

    # Loan Amount
    monto_field = page.locator("input[id*='LoanAmount']").first
    if monto_field.count() == 0:
        monto_field = page.get_by_role("textbox", name="Loan Amount").first
    monto_field.click()
    monto_field.fill("")
    monto_field.type(params["monto"])
    print(f"  Loan Amount: {params['monto']}")
    page.wait_for_timeout(500)

    # Duration
    duracion_field = page.locator("input[id*='Duration'], input[id*='duration']").first
    if duracion_field.count() == 0:
        duracion_field = page.get_by_role("textbox", name="Duration").first
    duracion_field.click()
    duracion_field.fill("")
    duracion_field.type(params["duracion"])
    print(f"  Duration: {params['duracion']}")

    # Duration unit (dropdown: Years/Months/Days)
    unidad = params["duracion_unidad"].capitalize()
    unit_select = page.locator("select[id*='Duration'], select[id*='duration']").first
    if unit_select.count() > 0:
        unit_select.select_option(label=unidad)
    else:
        unit_dropdown = page.locator(
            "span[id*='Duration'][class*='arrow'], "
            "div[id*='Duration'] .sapMSltArrow, "
            "span[id*='duration'][class*='arrow']"
        ).first
        if unit_dropdown.count() > 0:
            unit_dropdown.click()
            page.wait_for_timeout(500)
            page.get_by_role("option", name=unidad).click()
            page.wait_for_timeout(500)
    print(f"  Duration Unit: {unidad}")

    # Fixing Type
    if params.get("fixing_type"):
        fixing_select = page.locator(
            "select[id*='FixingType'], select[id*='fixingType']"
        ).first
        if fixing_select.count() > 0:
            fixing_select.select_option(label=params["fixing_type"])
        else:
            fixing_dropdown = page.locator(
                "[id*='FixingType'] .sapMSltArrow, "
                "[id*='fixingType'] .sapMSltArrow"
            ).first
            if fixing_dropdown.count() > 0:
                fixing_dropdown.click()
                page.wait_for_timeout(500)
                page.get_by_role("option", name=params["fixing_type"]).click()
                page.wait_for_timeout(500)
            else:
                # Fallback: click on the select-like element
                fixing_el = page.locator(
                    "[id*='FixingType'], [id*='fixingType']"
                ).first
                if fixing_el.count() > 0:
                    fixing_el.click()
                    page.wait_for_timeout(500)
                    page.get_by_text(params["fixing_type"], exact=False).first.click()
                    page.wait_for_timeout(500)
        print(f"  Fixing Type: {params['fixing_type']}")

    screenshot(page, "05_seccion_contract")

    # Click NEXT
    page.get_by_role("button", name="NEXT").click()
    page.wait_for_timeout(2000)
    print("  -> NEXT")


# ---------------------------------------------------------------------------
# Sección 2: Settlement
# ---------------------------------------------------------------------------

def llenar_seccion_settlement(page, params: dict):
    """Llena los campos de la sección 2. Settlement."""
    print("\n[Sección 2] Settlement")

    # Frequency
    freq_select = page.locator(
        "select[id*='Frequency'], select[id*='frequency']"
    ).first
    if freq_select.count() > 0:
        freq_select.select_option(label=params["frecuencia"])
    else:
        freq_el = page.locator(
            "[id*='Frequency'], [id*='frequency']"
        ).first
        if freq_el.count() > 0:
            freq_el.click()
            page.wait_for_timeout(500)
            page.get_by_role("option", name=params["frecuencia"]).click()
            page.wait_for_timeout(500)
    print(f"  Frequency: {params['frecuencia']}")

    # Key Date
    keydate_select = page.locator(
        "select[id*='KeyDate'], select[id*='keyDate']"
    ).first
    if keydate_select.count() > 0:
        keydate_select.select_option(label=params["key_date"])
    else:
        keydate_el = page.locator(
            "[id*='KeyDate'], [id*='keyDate']"
        ).first
        if keydate_el.count() > 0:
            keydate_el.click()
            page.wait_for_timeout(500)
            page.get_by_role("option", name=params["key_date"]).click()
            page.wait_for_timeout(500)
    print(f"  Key Date: {params['key_date']}")

    screenshot(page, "06_seccion_settlement")

    # Click NEXT
    page.get_by_role("button", name="NEXT").click()
    page.wait_for_timeout(2000)
    print("  -> NEXT")


# ---------------------------------------------------------------------------
# Sección 3: Conditions
# ---------------------------------------------------------------------------

def llenar_seccion_conditions(page, params: dict):
    """Llena los campos de la sección 3. Conditions."""
    print("\n[Sección 3] Conditions")

    # Nominal Interest Rate
    interest_field = page.locator(
        "input[id*='NominalInterest'], input[id*='nominalInterest'], "
        "input[id*='InterestRate'], input[id*='interestRate']"
    ).first
    if interest_field.count() == 0:
        interest_field = page.get_by_role(
            "textbox", name="Enter % Rate"
        ).first
    if interest_field.count() > 0:
        interest_field.click()
        interest_field.fill("")
        interest_field.type(params["tasa_interes"])
        print(f"  Nominal Interest: {params['tasa_interes']}%")
    else:
        print("  [WARN] Campo de tasa de interés no encontrado")

    screenshot(page, "07_seccion_conditions")

    # Click NEXT
    page.get_by_role("button", name="NEXT").click()
    page.wait_for_timeout(2000)
    print("  -> NEXT")


# ---------------------------------------------------------------------------
# Sección 4: Parties Roles (se omite)
# ---------------------------------------------------------------------------

def saltar_seccion_parties(page):
    """Omite la sección 4. Parties Roles sin llenar campos."""
    print("\n[Sección 4] Parties Roles — omitida")
    screenshot(page, "08_seccion_parties")
    page.get_by_role("button", name="NEXT").click()
    page.wait_for_timeout(2000)
    print("  -> NEXT")


# ---------------------------------------------------------------------------
# Sección 5: Additional Loan Details
# ---------------------------------------------------------------------------

def _seleccionar_dropdown(page, id_patterns: list, valor: str, label: str):
    """Intenta seleccionar un valor en un dropdown SAP por múltiples patrones de ID."""
    for pattern in id_patterns:
        el = page.locator(f"[id*='{pattern}']").first
        if el.count() > 0:
            el.click()
            page.wait_for_timeout(500)
            option = page.get_by_role("option", name=valor)
            if option.count() > 0:
                option.first.click()
                page.wait_for_timeout(500)
                print(f"  {label}: {valor}")
                return True
            # Si no encontró la opción exacta, intentar con texto parcial
            option_partial = page.locator(
                f"li:has-text('{valor}'), div[role='option']:has-text('{valor}')"
            ).first
            if option_partial.count() > 0:
                option_partial.click()
                page.wait_for_timeout(500)
                print(f"  {label}: {valor} (parcial)")
                return True
            # Cerrar el dropdown si no encontró nada
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
    print(f"  [WARN] No se pudo seleccionar {label}: {valor}")
    return False


def llenar_seccion_additional(page, params: dict):
    """Llena los campos de la sección 5. Additional Loan Details."""
    print("\n[Sección 5] Additional Loan Details")

    _seleccionar_dropdown(
        page, ["SalesProduct", "salesProduct"],
        params["sales_product"], "Sales Product"
    )
    _seleccionar_dropdown(
        page, ["Income", "income"],
        params["income"], "Income"
    )
    _seleccionar_dropdown(
        page, ["FECIIndicator", "feciIndicator", "FECI"],
        params["feci_indicator"], "FECI Indicator"
    )
    _seleccionar_dropdown(
        page, ["PreferentialIndicator", "preferentialIndicator", "Preferential"],
        params["preferential_indicator"], "Preferential Indicator"
    )
    _seleccionar_dropdown(
        page, ["LoanClassification", "loanClassification"],
        params["loan_classification"], "Loan Classification"
    )
    _seleccionar_dropdown(
        page, ["CINUActivityType", "cinuActivityType", "CINU"],
        params["cinu_activity_type"], "CINU Activity Type"
    )

    screenshot(page, "09_seccion_additional")

    # Click NEXT
    page.get_by_role("button", name="NEXT").click()
    page.wait_for_timeout(2000)
    print("  -> NEXT")


# ---------------------------------------------------------------------------
# Sección 6: Payment Party
# ---------------------------------------------------------------------------

def llenar_seccion_payment(page, params: dict):
    """Llena los campos de la sección 6. Payment Party."""
    print("\n[Sección 6] Payment Party")

    # Region Code
    _seleccionar_dropdown(
        page, ["RegionCode", "regionCode", "Region"],
        params["region_code"], "Region Code"
    )

    # Direct Debit/Disbursement Account
    cuenta = params["cuenta_debito"]
    acct_el = page.locator(
        "[id*='DisbursementAccount'], [id*='disbursementAccount'], "
        "[id*='DirectDebit'], [id*='directDebit']"
    ).first
    if acct_el.count() > 0:
        acct_el.click()
        page.wait_for_timeout(1000)
        # Buscar la cuenta en el dropdown
        option = page.locator(f"li:has-text('{cuenta}')").first
        if option.count() > 0:
            option.scroll_into_view_if_needed()
            option.click()
            print(f"  Disbursement Account: {cuenta}")
        else:
            # Scroll para buscar la cuenta
            listbox = page.locator("[role='listbox']").first
            if listbox.count() > 0:
                for _ in range(20):
                    option = page.locator(f"li:has-text('{cuenta}')").first
                    if option.count() > 0:
                        option.click()
                        print(f"  Disbursement Account: {cuenta}")
                        break
                    page.keyboard.press("ArrowDown")
                    page.wait_for_timeout(200)
                else:
                    print(f"  [WARN] Cuenta {cuenta} no encontrada en el listado")
    else:
        print("  [WARN] Campo de Disbursement Account no encontrado")

    page.wait_for_timeout(1000)
    screenshot(page, "10_seccion_payment")


# ---------------------------------------------------------------------------
# Calculate y CREATE LOAN
# ---------------------------------------------------------------------------

def calcular_y_crear(page) -> str:
    """
    Ejecuta Calculate, espera la simulación, crea el contrato
    y extrae el Loan Contract ID.
    """
    print("\n[Final] Calculando y creando contrato...")

    # 1. Click Calculate
    page.get_by_role("button", name="Calculate").click()
    print("  Calculate clickeado, esperando simulación...")
    time.sleep(6)
    screenshot(page, "11_simulacion")

    # 2. Click CREATE LOAN
    create_btn = page.get_by_role("button", name="CREATE LOAN")
    create_btn.wait_for(state="visible", timeout=30000)
    create_btn.click()
    print("  CREATE LOAN clickeado, esperando creación...")
    time.sleep(6)
    screenshot(page, "12_contrato_creado")

    # 3. Extraer el ID del contrato
    selector_id = (
        "#application-ZBAOLBLACCRT_O-display-component"
        "---detail--LoanContractID-text"
    )
    try:
        page.wait_for_function(
            """selector => {
                const el = document.querySelector(selector);
                return el && el.innerText.trim().length > 0;
            }""",
            arg=selector_id,
            timeout=30000,
        )
        elemento_contrato = page.locator(selector_id)
        loan_contract_id = elemento_contrato.inner_text().strip()
    except PwTimeout:
        # Fallback: buscar en otros elementos del header
        print("  [Aviso] Selector principal no encontrado, buscando alternativo...")
        try:
            alt = page.locator("[id*='LoanContractID']").first
            alt.wait_for(state="visible", timeout=10000)
            loan_contract_id = alt.inner_text().strip()
        except PwTimeout:
            loan_contract_id = "NO_CAPTURADO"

    screenshot(page, "13_id_contrato_final")

    print("\n" + "=" * 60)
    print(f"  CONTRATO CREADO EXITOSAMENTE")
    print(f"  Loan Contract ID: {loan_contract_id}")
    print("=" * 60)

    return loan_contract_id


# ---------------------------------------------------------------------------
# Flujo principal de creación de contrato
# ---------------------------------------------------------------------------

def crear_contrato(page, params: dict) -> str:
    """
    Ejecuta el flujo completo de creación de contrato de préstamo.
    Retorna el Loan Contract ID.
    """

    # --- Paso 1: Navegar a Loan Accounts ---
    print("\n[Paso 1] Navegando a 'Loan Accounts'...")
    more_groups = page.get_by_label("More groups")
    more_groups.wait_for(state="visible", timeout=10000)
    more_groups.click()
    page.wait_for_timeout(2000)

    loan_link = page.locator("text=Loan Accounts").first
    loan_link.wait_for(state="visible", timeout=10000)
    loan_link.click()
    page.wait_for_timeout(2000)
    screenshot(page, "01_loan_accounts")

    # --- Paso 2: Abrir Loan Contract Create ---
    print("[Paso 2] Abriendo 'Loan Contract - Create'...")
    tile = page.get_by_role("link", name="Loan Contract Create").first
    if tile.count() == 0:
        tile = page.locator("text=Loan Contract").first
    tile.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)
    screenshot(page, "02_loan_contract_create")

    # --- Paso 3: Buscar cliente ---
    id_cliente = params["id_cliente"]
    print(f"[Paso 3] Buscando cliente: {id_cliente}")
    customer_field = page.get_by_role("textbox", name="Customer No")
    customer_field.click()
    customer_field.fill(str(id_cliente))
    page.get_by_role("button", name="Search", exact=True).click()
    page.wait_for_timeout(3000)

    # Seleccionar resultado
    page.get_by_text(str(id_cliente)).first.click()
    page.wait_for_timeout(3000)
    screenshot(page, "03_cliente_seleccionado")

    # --- Paso 4: Click Create y seleccionar fecha ---
    print("[Paso 4] Creando nuevo contrato...")
    btn_create = page.get_by_role("button", name="Create", exact=True)
    btn_create.wait_for(state="attached", timeout=10000)
    time.sleep(3)
    btn_create.click()
    page.wait_for_timeout(2000)

    # Seleccionar fecha de inicio
    print(f"[Paso 5] Seleccionando fecha: {params['fecha_inicio']}")
    seleccionar_fecha_contrato(page, params["fecha_inicio"])
    page.wait_for_timeout(1000)

    # Click Continue
    page.get_by_role("button", name="Continue", exact=True).click()
    page.wait_for_timeout(3000)

    # --- Paso 6: Seleccionar Manager (primera opción) ---
    print("[Paso 6] Seleccionando Manager...")
    manager_item = page.locator("div.sapMSLIDescription").first
    manager_item.wait_for(state="visible", timeout=10000)
    manager_item.click()
    page.wait_for_timeout(3000)

    # --- Paso 7: Seleccionar Producto ---
    print(f"[Paso 7] Seleccionando producto: {params['producto']}")
    product_item = page.locator("span[id$='-titleText-inner']").filter(
        has_text=params["producto"]
    ).first
    product_item.scroll_into_view_if_needed()
    product_item.click(force=True)
    page.wait_for_timeout(3000)
    screenshot(page, "04_producto_seleccionado")

    # --- Secciones 1-6 del formulario ---
    llenar_seccion_contract(page, params)
    llenar_seccion_settlement(page, params)
    llenar_seccion_conditions(page, params)
    saltar_seccion_parties(page)
    llenar_seccion_additional(page, params)
    llenar_seccion_payment(page, params)

    # --- Calculate y CREATE LOAN ---
    loan_id = calcular_y_crear(page)

    return loan_id


# ---------------------------------------------------------------------------
# Verificación de sesión SAP
# ---------------------------------------------------------------------------

def verificar_sesion_sap(page):
    """Verifica que estamos en Shell Home; si no, navega e intenta login."""
    print("[Verificación] Comprobando sesión SAP...")
    current_url = page.url

    if "10.165.6.8" not in current_url or "Shell-home" not in current_url:
        print("[Navegación] Navegando a SAP Fiori Launchpad...")
        page.goto(SAP_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

    try:
        shell_header = page.locator("#shell-header")
        shell_header.wait_for(state="visible", timeout=10000)
        print("[OK] Sesión SAP activa — Shell Home visible")
    except PwTimeout:
        print("[Login] Sesión expirada. Ingresando credenciales...")
        import os
        sap_user = os.environ.get("SAP_USER", "")
        sap_password = os.environ.get("SAP_PASSWORD", "")
        if not sap_user or not sap_password:
            print("[ERROR] SAP_USER y SAP_PASSWORD deben estar configurados.")
            sys.exit(1)
        page.get_by_role("textbox", name="User").fill(sap_user)
        page.get_by_role("textbox", name="Password").fill(sap_password)
        page.get_by_role("button", name="Log On").click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        # Verificar login exitoso
        try:
            page.locator("#shell-header").wait_for(state="visible", timeout=15000)
            print("[OK] Login exitoso — Shell Home visible")
        except PwTimeout:
            print("[ERROR] Login fallido. Verifique credenciales.")
            screenshot(page, "error_login")
            sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    params = solicitar_parametros()
    start_time = datetime.now()

    with sync_playwright() as p:
        print("\n[Conexión] Conectando al Chrome del escritorio vía CDP...")
        browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        page.on("dialog", lambda dialog: dialog.accept())

        verificar_sesion_sap(page)
        screenshot(page, "00_sap_home")

        try:
            loan_id = crear_contrato(page, params)
        except Exception as exc:
            print(f"\n[ERROR] Error durante la creación del contrato: {exc}")
            try:
                screenshot(page, "error_creacion_contrato")
            except Exception:
                print("[ERROR] No se pudo capturar screenshot de error")
            traceback.print_exc()
            loan_id = "ERROR"

    end_time = datetime.now()
    duracion = (end_time - start_time).total_seconds()

    print(f"\n[Recursos] Tiempo de ejecución: {duracion:.1f} s")
    print(f"\n[OUTPUT] Loan Contract ID: {loan_id}")

    return loan_id


if __name__ == "__main__":
    resultado = main()
    sys.exit(
        0 if resultado and resultado not in ("ERROR", "NO_CAPTURADO") else 1
    )
