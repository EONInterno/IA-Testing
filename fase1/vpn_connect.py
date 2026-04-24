"""
Fase 1 — Conexión VPN Cisco AnyConnect / openconnect
Conecta a la VPN corporativa y verifica acceso a la red SAP.
"""

import os
import subprocess
import shutil
import time
from datetime import datetime
from pathlib import Path

EVIDENCE_DIR = Path(__file__).parent / "evidencia" / "screenshots"
CISCO_BIN = "/opt/cisco/anyconnect/bin/vpn"


def _ensure_evidence_dir():
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def _cisco_available() -> bool:
    return shutil.which(CISCO_BIN) is not None or Path(CISCO_BIN).exists()


def _install_openconnect():
    print("[VPN] Cisco AnyConnect no encontrado. Instalando openconnect...")
    subprocess.run(
        ["sudo", "apt-get", "update", "-qq"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["sudo", "apt-get", "install", "-y", "openconnect"],
        check=True,
        capture_output=True,
    )
    print("[VPN] openconnect instalado correctamente.")


def connect_vpn(host: str, user: str, password: str) -> bool:
    """
    Conecta a la VPN usando Cisco AnyConnect o openconnect como fallback.
    Retorna True si la conexión fue exitosa.
    """
    _ensure_evidence_dir()

    if _cisco_available():
        return _connect_cisco(host, user, password)
    else:
        _install_openconnect()
        return _connect_openconnect(host, user, password)


def _connect_cisco(host: str, user: str, password: str) -> bool:
    print(f"[VPN] Conectando con Cisco AnyConnect a {host}...")
    input_data = f"connect {host}\n{user}\n{password}\ny\n"
    try:
        proc = subprocess.Popen(
            [CISCO_BIN, "-s"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = proc.communicate(input=input_data, timeout=60)
        log = stdout + "\n" + stderr
        _save_connection_log(log)

        print("Credenciales VPN enviadas. Por favor aprueba el MFA en tu dispositivo.")
        time.sleep(30)

        return _verify_connection(host)
    except Exception as exc:
        print(f"[VPN] Error con Cisco AnyConnect: {exc}")
        return False


def _connect_openconnect(host: str, user: str, password: str) -> bool:
    print(f"[VPN] Conectando con openconnect a {host}...")
    try:
        proc = subprocess.Popen(
            [
                "sudo", "openconnect",
                "--user", user,
                "--passwd-on-stdin",
                "--no-dtls",
                "--servercert", "pin-sha256:ACCEPT",
                host,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Send password and leave the process running in background
        proc.stdin.write(password + "\n")
        proc.stdin.flush()

        print("Credenciales VPN enviadas. Por favor aprueba el MFA en tu dispositivo.")
        time.sleep(30)

        # Check if process is still running (good sign for VPN)
        if proc.poll() is not None:
            stdout, stderr = proc.communicate()
            log = stdout + "\n" + stderr
            _save_connection_log(log)
            print(f"[VPN] openconnect terminó inesperadamente:\n{log}")
            return False

        _save_connection_log("[VPN] openconnect corriendo en segundo plano.")
        return _verify_connection(host)
    except Exception as exc:
        print(f"[VPN] Error con openconnect: {exc}")
        return False


def _verify_connection(host: str) -> bool:
    """Verifica conectividad haciendo curl a la IP del servidor SAP."""
    target = "10.165.6.8"
    print(f"[VPN] Verificando conectividad a {target}...")

    # Try curl first (more reliable than ping which may be blocked)
    try:
        result = subprocess.run(
            ["curl", "-sk", "--connect-timeout", "10",
             f"https://{target}:44300/"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 or "SSL" in result.stderr or "html" in result.stdout.lower():
            print(f"[VPN] ✓ Conexión exitosa a {target}")
            _save_evidence_screenshot(True, target)
            return True
    except Exception:
        pass

    # Fallback to ping
    try:
        result = subprocess.run(
            ["ping", "-c", "3", "-W", "5", target],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode == 0:
            print(f"[VPN] ✓ Ping exitoso a {target}")
            _save_evidence_screenshot(True, target)
            return True
    except Exception:
        pass

    print(f"[VPN] ✗ No se pudo conectar a {target}")
    _save_evidence_screenshot(False, target)
    return False


def _save_connection_log(log: str):
    log_path = EVIDENCE_DIR.parent / "vpn_connection.log"
    with open(log_path, "w") as f:
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(log)
    print(f"[VPN] Log guardado en {log_path}")


def _save_evidence_screenshot(success: bool, target: str):
    """Guarda evidencia de la conexión VPN como archivo de texto/log."""
    evidence_path = EVIDENCE_DIR / "01_vpn_connected.png"
    # Since we can't take a GUI screenshot from a script,
    # we generate a text-based evidence file.
    # The actual screenshot will be taken by main.py using Playwright if needed.
    log_path = EVIDENCE_DIR.parent / "vpn_status.txt"
    status = "EXITOSA" if success else "FALLIDA"
    with open(log_path, "w") as f:
        f.write(f"=== Estado de Conexión VPN ===\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Target: {target}\n")
        f.write(f"Estado: {status}\n")
    print(f"[VPN] Evidencia guardada en {log_path}")
