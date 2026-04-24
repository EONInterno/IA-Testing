"""
Fase 1 — Login a SAP Fiori con Playwright (síncrono)
Navega al launchpad de SAP Fiori, ingresa credenciales y verifica acceso al Shell Home.
"""

import os
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

SAP_URL = "https://10.165.6.8:44300/sap/bc/ui2/flp?sap-client=110&sap-language=EN#Shell-home"
SCREENSHOTS_DIR = Path(__file__).parent / "evidencia" / "screenshots"
VIDEOS_DIR = Path(__file__).parent / "evidencia" / "videos"

# Possible selectors for SAP Fiori login fields
USER_SELECTORS = [
    'input[name="sap-user"]',
    '#USERNAME_FIELD input',
    '#USERNAME_BLOCK input',
    'input[id*="USER"]',
    'input[id*="user"]',
    'input[placeholder*="User"]',
    'input[type="text"]',
]

PASS_SELECTORS = [
    'input[name="sap-password"]',
    '#PASSWORD_FIELD input',
    '#PASSWORD_BLOCK input',
    'input[id*="PASS"]',
    'input[id*="pass"]',
    'input[placeholder*="Pass"]',
    'input[type="password"]',
]

LOGIN_BTN_SELECTORS = [
    'button:has-text("Log On")',
    'button:has-text("Iniciar")',
    'button:has-text("Login")',
    '#LOGIN_LINK',
    'input[type="submit"]',
    'button[type="submit"]',
]


def _ensure_dirs():
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


def _find_element(page, selectors: list, description: str, timeout: int = 30000):
    """Try multiple selectors and return the first one found."""
    for selector in selectors:
        try:
            element = page.wait_for_selector(selector, timeout=5000)
            if element:
                print(f"[SAP] Campo '{description}' encontrado con selector: {selector}")
                return element
        except PwTimeout:
            continue

    # Last resort: wait longer with first selector
    print(f"[SAP] Intentando selector principal con timeout extendido para '{description}'...")
    try:
        element = page.wait_for_selector(selectors[0], timeout=timeout)
        return element
    except PwTimeout:
        # Dump available inputs for debugging
        inputs = page.query_selector_all("input")
        print(f"[SAP] Inputs disponibles en la página:")
        for inp in inputs:
            attrs = page.evaluate(
                """(el) => {
                    const obj = {};
                    for (const attr of el.attributes) obj[attr.name] = attr.value;
                    return obj;
                }""",
                inp,
            )
            print(f"  - {attrs}")
        raise Exception(
            f"No se encontró el campo '{description}' con ningún selector conocido."
        )


def login_sap(sap_user: str, sap_password: str) -> bool:
    """
    Abre SAP Fiori, ingresa credenciales y verifica que cargue el Shell Home.
    Retorna True si el login fue exitoso.
    """
    _ensure_dirs()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--ignore-certificate-errors", "--no-sandbox"],
        )
        context = browser.new_context(
            ignore_https_errors=True,
            record_video_dir=str(VIDEOS_DIR),
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        try:
            success = _perform_login(page, sap_user, sap_password)
        except Exception as exc:
            print(f"[SAP] Error durante login: {exc}")
            page.screenshot(path=str(SCREENSHOTS_DIR / "error_sap_login.png"))
            success = False
        finally:
            context.close()
            browser.close()

    return success


def _perform_login(page, sap_user: str, sap_password: str) -> bool:
    # Step 1: Navigate to SAP Fiori
    print(f"[SAP] Navegando a {SAP_URL}...")
    page.goto(SAP_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    page.screenshot(path=str(SCREENSHOTS_DIR / "02_sap_login_page.png"))
    print("[SAP] Screenshot: 02_sap_login_page.png")

    # Step 2: Find and fill username
    print("[SAP] Buscando campo de usuario...")
    user_field = _find_element(page, USER_SELECTORS, "Usuario")
    user_field.click()
    user_field.fill(sap_user)

    # Step 3: Find and fill password
    print("[SAP] Buscando campo de contraseña...")
    pass_field = _find_element(page, PASS_SELECTORS, "Contraseña")
    pass_field.click()
    pass_field.fill(sap_password)

    # Take screenshot with credentials entered (password is masked by browser)
    page.screenshot(path=str(SCREENSHOTS_DIR / "03_sap_credentials_entered.png"))
    print("[SAP] Screenshot: 03_sap_credentials_entered.png")

    # Step 4: Click login button
    print("[SAP] Buscando botón de login...")
    login_btn = _find_element(page, LOGIN_BTN_SELECTORS, "Botón Login")
    login_btn.click()

    # Step 5: Wait for Shell Home to load
    print("[SAP] Esperando carga del Shell Home...")
    shell_selectors = [
        "#shell-header",
        "#shell--header",
        "[id*='shell']",
        ".sapUshellShellHead",
        "#meAreaHeaderButton",
    ]

    shell_loaded = False
    for selector in shell_selectors:
        try:
            page.wait_for_selector(selector, timeout=30000)
            print(f"[SAP] Shell Home detectado con selector: {selector}")
            shell_loaded = True
            break
        except PwTimeout:
            continue

    if not shell_loaded:
        # Check if we're still on login page (wrong credentials)
        print("[SAP] No se detectó Shell Home. Verificando estado de la página...")
        page.screenshot(path=str(SCREENSHOTS_DIR / "error_after_login.png"))
        current_url = page.url
        print(f"[SAP] URL actual: {current_url}")
        return False

    page.wait_for_timeout(3000)
    page.screenshot(path=str(SCREENSHOTS_DIR / "04_sap_home_loaded.png"))
    print("[SAP] Screenshot: 04_sap_home_loaded.png")
    print("[SAP] ✓ Login exitoso - Shell Home cargado")
    return True
