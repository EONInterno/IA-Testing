"""
Fase 1 — Orquestador principal
Ejecuta la conexión VPN y luego el login a SAP Fiori.
Genera un reporte con los resultados y la evidencia recopilada.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Ensure fase1 package is importable
sys.path.insert(0, str(Path(__file__).parent))

from vpn_connect import connect_vpn
from sap_login import login_sap

EVIDENCE_DIR = Path(__file__).parent / "evidencia"
REPORT_PATH = EVIDENCE_DIR / "reporte_fase1.txt"


def get_credentials():
    """Lee las credenciales de variables de entorno."""
    vpn_host = os.environ.get("VPN_HOST")
    vpn_user = os.environ.get("VPN_USER")
    vpn_password = os.environ.get("VPN_PASSWORD")
    sap_user = os.environ.get("SAP_USER")
    sap_password = os.environ.get("SAP_PASSWORD")

    missing = []
    if not vpn_host:
        missing.append("VPN_HOST")
    if not vpn_user:
        missing.append("VPN_USER")
    if not vpn_password:
        missing.append("VPN_PASSWORD")
    if not sap_user:
        missing.append("SAP_USER")
    if not sap_password:
        missing.append("SAP_PASSWORD")

    if missing:
        print(f"[ERROR] Variables de entorno faltantes: {', '.join(missing)}")
        print("Configure las variables antes de ejecutar:")
        for var in missing:
            print(f"  export {var}='...'")
        sys.exit(1)

    return vpn_host, vpn_user, vpn_password, sap_user, sap_password


def collect_evidence() -> list:
    """Recopila la lista de archivos de evidencia generados."""
    evidence_files = []
    for path in sorted(EVIDENCE_DIR.rglob("*")):
        if path.is_file() and path.name != "reporte_fase1.txt":
            evidence_files.append(str(path.relative_to(EVIDENCE_DIR)))
    return evidence_files


def generate_report(
    start_time: datetime,
    end_time: datetime,
    vpn_status: bool,
    sap_status: bool,
    evidence_files: list,
):
    """Genera el reporte de la Fase 1."""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    duration = (end_time - start_time).total_seconds()

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("  REPORTE FASE 1 — Conexión VPN y Login SAP Fiori\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Timestamp inicio : {start_time.isoformat()}\n")
        f.write(f"Timestamp fin    : {end_time.isoformat()}\n")
        f.write(f"Duración total   : {duration:.1f} segundos\n\n")
        f.write(f"Estado VPN       : {'EXITOSO' if vpn_status else 'FALLIDO'}\n")
        f.write(f"Estado Login SAP : {'EXITOSO' if sap_status else 'FALLIDO'}\n\n")
        f.write("Archivos de evidencia generados:\n")
        for ef in evidence_files:
            f.write(f"  - {ef}\n")
        f.write(f"\nRecursos utilizados:\n")
        f.write(f"  Tiempo total de ejecución: {duration:.1f} s\n")

        try:
            import resource
            mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            f.write(f"  Memoria máxima (RSS)     : {mem} KB\n")
        except Exception:
            f.write(f"  Memoria máxima (RSS)     : no disponible\n")

        f.write("\n" + "=" * 60 + "\n")

    print(f"\n[REPORTE] Guardado en {REPORT_PATH}")


def main():
    print("=" * 60)
    print("  FASE 1 — Conexión VPN y Login SAP Fiori")
    print("=" * 60)

    start_time = datetime.now()

    # Read credentials from environment
    vpn_host, vpn_user, vpn_password, sap_user, sap_password = get_credentials()

    # Step 1: VPN Connection
    print("\n--- Paso 1: Conexión VPN ---")
    vpn_ok = connect_vpn(vpn_host, vpn_user, vpn_password)

    if not vpn_ok:
        print("\n[ERROR] La conexión VPN falló. No se puede continuar con el login SAP.")
        sap_ok = False
    else:
        # Step 2: SAP Login
        print("\n--- Paso 2: Login SAP Fiori ---")
        sap_ok = login_sap(sap_user, sap_password)

    # Step 3: Generate report
    end_time = datetime.now()
    evidence_files = collect_evidence()
    generate_report(start_time, end_time, vpn_ok, sap_ok, evidence_files)

    # Summary
    print("\n--- Resumen ---")
    print(f"VPN      : {'✓ Conectada' if vpn_ok else '✗ Fallida'}")
    print(f"SAP Login: {'✓ Exitoso' if sap_ok else '✗ Fallido'}")
    print(f"Evidencia: {len(evidence_files)} archivos generados")
    print("=" * 60)

    return vpn_ok and sap_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
