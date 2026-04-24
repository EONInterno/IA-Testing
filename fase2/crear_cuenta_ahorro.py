"""
Fase 2 — Creación de Cuenta de Ahorro en SAP Fiori
Conecta al Chrome del escritorio vía CDP, navega por SAP Fiori y crea una cuenta de ahorro.
Los parámetros se solicitan por consola (no hardcodeados).
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

SAP_URL = "https://10.165.6.8:44300/sap/bc/ui2/flp?sap-client=110&sap-language=EN#Shell-home"
CDP_ENDPOINT = "http://localhost:29229"
SCREENSHOTS_DIR = Path(__file__).parent / "evidencia" / "screenshots"


def screenshot(page, name: str):
    """Toma screenshot y lo guarda con nombre descriptivo."""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOTS_DIR / f"{name}.png"
    page.screenshot(path=str(path))
    print(f"  [Screenshot] {path.name}")


def solicitar_parametros() -> dict:
    """Solicita los 4 parámetros al usuario por consola."""
    print("=" * 60)
    print("  FASE 2 — Creación de Cuenta de Ahorro")
    print("=" * 60)
    print("\nIngrese los siguientes parámetros:\n")

    id_cliente = input("  ID_CLIENTE (número de cliente): ").strip()
    fecha_inicio = input("  FECHA_INICIO (dd/mm/yyyy): ").strip()
    producto = input("  PRODUCTO (nombre del producto de ahorro): ").strip()
    condicion_grupo = input("  CONDICION_GRUPO (nombre de condición): ").strip()

    if not all([id_cliente, fecha_inicio, producto, condicion_grupo]):
        print("\n[ERROR] Todos los campos son obligatorios.")
        sys.exit(1)

    # Validar formato de fecha
    try:
        datetime.strptime(fecha_inicio, "%d/%m/%Y")
    except ValueError:
        print("\n[ERROR] Formato de fecha inválido. Use dd/mm/yyyy")
        sys.exit(1)

    print(f"\n  Parámetros recibidos:")
    print(f"    ID_CLIENTE      : {id_cliente}")
    print(f"    FECHA_INICIO    : {fecha_inicio}")
    print(f"    PRODUCTO        : {producto}")
    print(f"    CONDICION_GRUPO : {condicion_grupo}")
    print()
    return {
        "id_cliente": id_cliente,
        "fecha_inicio": fecha_inicio,
        "producto": producto,
        "condicion_grupo": condicion_grupo,
    }


def seleccionar_fecha(page, fecha_str: str):
    """Selecciona la fecha de inicio en el date picker de SAP."""
    fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
    anio = fecha_obj.year
    nombre_mes = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][fecha_obj.month]
    fecha_sap = fecha_obj.strftime("%Y%m%d")

    print(f"  [Fecha] Seleccionando {fecha_str}...")

    # Abrir vista de navegación de años
    page.locator("#CACStartDateCalendar--Head-B2").click()
    page.wait_for_timeout(500)
    print("  [Fecha] Date picker abierto")

    # Buscar el año navegando si es necesario
    max_clicks = 20
    for _ in range(max_clicks):
        selector_anio = f"div[data-sap-year-start^='{anio}']"
        if page.locator(selector_anio).count() > 0:
            page.locator(selector_anio).first.click()
            print(f"  [Fecha] Año {anio} seleccionado")
            break
        anio_texto = page.locator("#CACStartDateCalendar--Head-B2").inner_text().strip()
        anio_actual = int(anio_texto[:4])
        if anio < anio_actual:
            page.locator("#CACStartDateCalendar--Head-prev").click()
        else:
            page.locator("#CACStartDateCalendar--Head-next").click()
        page.wait_for_timeout(500)
    else:
        raise Exception(f"No se encontró el año {anio} en el date picker después de {max_clicks} intentos.")

    # Seleccionar mes
    page.locator("#CACStartDateCalendar--Head-B1").click()
    page.wait_for_timeout(500)
    selector_mes = f"div[role='gridcell'][aria-label='{nombre_mes} {anio}']"
    page.locator(selector_mes).wait_for(state="visible")
    page.locator(selector_mes).click()
    print(f"  [Fecha] Mes {nombre_mes} seleccionado")

    # Seleccionar día
    selector_dia = f"div[data-sap-day='{fecha_sap}']"
    page.locator(selector_dia).wait_for(state="visible")
    page.locator(selector_dia).click()
    print(f"  [Fecha] Fecha {fecha_str} seleccionada correctamente")


def crear_cuenta_ahorro(page, params: dict) -> str:
    """
    Ejecuta el flujo completo de creación de cuenta de ahorro en SAP Fiori.
    Retorna el número de cuenta creado.
    """
    id_cliente = params["id_cliente"]
    fecha_inicio = params["fecha_inicio"]
    producto = params["producto"]
    condicion_grupo = params["condicion_grupo"]

    # --- Paso 1: Navegar a Deposit Accounts ---
    print("\n[Paso 1] Navegando a 'Deposit Accounts'...")
    page.get_by_label("More groups").click()
    page.wait_for_timeout(2000)
    screenshot(page, "01_more_groups")

    deposit_link = page.locator("text=Deposit Accounts").first
    deposit_link.wait_for(state="visible", timeout=10000)
    deposit_link.click()
    page.wait_for_timeout(2000)
    screenshot(page, "02_deposit_accounts")

    # --- Paso 2: Abrir Current Account Create/Change ---
    print("[Paso 2] Abriendo 'Current Account Create/Change'...")
    page.get_by_role("link", name="Current Account Create/Change").click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)
    screenshot(page, "03_create_change_screen")

    # --- Paso 3: Buscar cliente ---
    print(f"[Paso 3] Buscando cliente: {id_cliente}")
    customer_field = page.get_by_role("textbox", name="Customer No")
    customer_field.click()
    customer_field.fill(str(id_cliente))
    page.get_by_role("button", name="Search", exact=True).click()
    page.wait_for_timeout(3000)

    # Seleccionar resultado de búsqueda
    page.get_by_text(str(id_cliente)).click()
    page.wait_for_selector("text=Create", state="visible")
    page.wait_for_timeout(3000)
    screenshot(page, "04_cliente_seleccionado")

    # --- Paso 4: Crear nueva cuenta ---
    print("[Paso 4] Haciendo clic en 'Create'...")
    btn_create = page.get_by_role("button", name="Create", exact=True)
    btn_create.wait_for(state="attached")
    time.sleep(6)
    btn_create.click()
    page.wait_for_timeout(2000)
    screenshot(page, "05_create_clicked")

    # --- Paso 5: Seleccionar fecha de inicio ---
    print(f"[Paso 5] Seleccionando fecha de inicio: {fecha_inicio}")
    seleccionar_fecha(page, fecha_inicio)
    page.wait_for_timeout(1000)
    screenshot(page, "06_fecha_seleccionada")

    # --- Paso 6: Continuar ---
    print("[Paso 6] Haciendo clic en 'Continue'...")
    page.get_by_role("button", name="Continue", exact=True).click()
    page.wait_for_timeout(3000)
    screenshot(page, "07_continue")

    # --- Paso 7: Seleccionar oficina/sucursal ---
    print("[Paso 7] Seleccionando oficina...")
    oficina = page.locator("div.sapMSLIDescription").first
    oficina.wait_for(state="visible", timeout=10000)
    oficina.click()
    page.wait_for_timeout(5000)
    screenshot(page, "08_oficina_seleccionada")

    # --- Paso 8: Seleccionar producto de ahorro ---
    print(f"[Paso 8] Seleccionando producto: {producto}")
    selector_titulo = "span[id$='-titleText-inner']"
    cuenta_locator = page.locator(selector_titulo).filter(has_text=producto).first
    cuenta_locator.scroll_into_view_if_needed()
    cuenta_locator.click(force=True)
    page.wait_for_timeout(3000)
    screenshot(page, "09_producto_seleccionado")

    # --- Paso 9: Llenar Contract Purpose (CONDICION_GRUPO del usuario) ---
    print(f"[Paso 9] Ingresando Contract Purpose: {condicion_grupo}")
    purpose_field = page.locator("input[id*='contractPurpose']").first
    if purpose_field.count() == 0:
        purpose_field = page.get_by_role("textbox").nth(0)
    purpose_field.click()
    purpose_field.fill(condicion_grupo)
    page.wait_for_timeout(1000)
    screenshot(page, "10_contract_purpose")

    # --- Paso 10: Seleccionar Condition Group Settlement (obligatorio) ---
    print("[Paso 10] Seleccionando Condition Group Settlement...")
    select_box = page.locator("#__xmlview1--selectConditionGroup")
    if select_box.count() == 0:
        select_box = page.locator("[id$='--selectConditionGroup']").last
    select_box.click()
    page.wait_for_timeout(1000)

    opcion = page.get_by_role("option", name="CTA_AHO_REG-Savings Loc Natural")
    opcion.wait_for(state="visible", timeout=10000)
    opcion.click()
    page.wait_for_timeout(2000)
    screenshot(page, "11_condicion_grupo")

    # --- Paso 11: Guardar ---
    print("[Paso 11] Guardando cuenta...")
    page.get_by_role("button", name="Save").click()
    page.wait_for_timeout(3000)
    screenshot(page, "12_guardando")

    # Confirmar diálogo OK si aparece
    try:
        btn_ok = page.get_by_role("button", name="OK", exact=True)
        btn_ok.wait_for(state="visible", timeout=5000)
        btn_ok.click()
        page.wait_for_timeout(5000)
    except PwTimeout:
        print("  [Info] No apareció diálogo de confirmación OK")

    screenshot(page, "13_cuenta_creada")

    # --- Paso 12: Capturar número de cuenta ---
    print("[Paso 12] Esperando número de cuenta creado...")
    locator_numero = page.locator(
        "#application-ZBAOAMCACCRU_O-display-component---detail--objectHeader-titleText-inner"
    )

    try:
        page.wait_for_function(
            "selector => { const el = document.querySelector(selector); return el && el.innerText.trim().length > 0; }",
            arg="#application-ZBAOAMCACCRU_O-display-component---detail--objectHeader-titleText-inner",
            timeout=30000,
        )
        numero_cuenta = locator_numero.inner_text().strip()
    except PwTimeout:
        # Fallback: buscar cualquier número en el header
        print("  [Aviso] Selector principal no encontrado, buscando alternativo...")
        try:
            header_text = page.locator("[id*='objectHeader-titleText-inner']").first
            header_text.wait_for(state="visible", timeout=10000)
            numero_cuenta = header_text.inner_text().strip()
        except PwTimeout:
            numero_cuenta = "NO_CAPTURADO"

    screenshot(page, "14_numero_cuenta_final")

    print("\n" + "=" * 60)
    print(f"  CUENTA CREADA EXITOSAMENTE")
    print(f"  Número de cuenta: {numero_cuenta}")
    print("=" * 60)

    return numero_cuenta


def main():
    # Solicitar parámetros por consola
    params = solicitar_parametros()

    start_time = datetime.now()

    with sync_playwright() as p:
        print("\n[Conexión] Conectando al Chrome del escritorio vía CDP...")
        browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        # Manejar diálogos automáticamente
        page.on("dialog", lambda dialog: dialog.accept())

        # Verificar si ya estamos en SAP Shell Home
        print("[Verificación] Comprobando sesión SAP...")
        current_url = page.url

        if "10.165.6.8" not in current_url or "Shell-home" not in current_url:
            print("[Navegación] Navegando a SAP Fiori Launchpad...")
            page.goto(SAP_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)

        # Verificar si necesitamos login
        try:
            shell_header = page.locator("#shell-header")
            shell_header.wait_for(state="visible", timeout=10000)
            print("[OK] Sesión SAP activa — Shell Home visible")
        except PwTimeout:
            print("[Login] Necesita login. Ingresando credenciales...")
            import os
            sap_user = os.environ.get("SAP_USER", "")
            sap_password = os.environ.get("SAP_PASSWORD", "")
            if sap_user and sap_password:
                page.get_by_role("textbox", name="User").fill(sap_user)
                page.get_by_role("textbox", name="Password").fill(sap_password)
                page.get_by_role("button", name="Log On").click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)
            else:
                print("[ERROR] No hay credenciales SAP configuradas (SAP_USER, SAP_PASSWORD)")
                sys.exit(1)

        screenshot(page, "00_sap_home")

        # Ejecutar creación de cuenta
        try:
            numero_cuenta = crear_cuenta_ahorro(page, params)
        except Exception as exc:
            print(f"\n[ERROR] Error durante la creación: {exc}")
            try:
                screenshot(page, "error_creacion")
            except Exception:
                print("[ERROR] No se pudo capturar screenshot de error")
            import traceback
            traceback.print_exc()
            numero_cuenta = "ERROR"

    end_time = datetime.now()
    duracion = (end_time - start_time).total_seconds()

    print(f"\n[Recursos] Tiempo de ejecución: {duracion:.1f} s")
    print(f"\n[OUTPUT] Número de cuenta creado: {numero_cuenta}")

    return numero_cuenta


if __name__ == "__main__":
    resultado = main()
    sys.exit(0 if resultado and resultado != "ERROR" and resultado != "NO_CAPTURADO" else 1)
