# Fase 2 — Creación de Cuenta de Ahorro en SAP Fiori

Script de automatización para crear cuentas de ahorro en SAP Fiori usando Playwright vía CDP.

## Requisitos

- Python 3.9+
- Playwright instalado (`pip install playwright && python -m playwright install chromium`)
- Chrome ejecutándose con CDP en `localhost:29229`
- VPN conectada al servidor SAP (`10.165.6.8:44300`)
- Sesión SAP activa (o credenciales SAP en variables de entorno `SAP_USER`, `SAP_PASSWORD`)

## Parámetros

El script solicita 4 parámetros por consola (no hardcodeados):

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `ID_CLIENTE` | Número de cliente SAP | `1000430` |
| `FECHA_INICIO` | Fecha de inicio (dd/mm/yyyy) | `24/10/2005` |
| `PRODUCTO` | Nombre del producto de ahorro | `Cuenta De Ahorro Pacific Bank` |
| `CONDICION_GRUPO` | Propósito del contrato | `Test Devin` |

## Ejecución

```bash
python fase2/crear_cuenta_ahorro.py
```

## Flujo del Script

1. Conecta al Chrome del escritorio vía CDP (visible en Desktop)
2. Verifica sesión SAP activa, hace login si es necesario
3. Navega: More Groups → Deposit Accounts → Current Account Create/Change
4. Busca el cliente por ID
5. Crea nueva cuenta (botón Create)
6. Selecciona fecha de inicio en el date picker
7. Selecciona oficina/sucursal
8. Selecciona producto de ahorro
9. Llena Contract Purpose con CONDICION_GRUPO
10. Selecciona Condition Group Settlement (CTA_AHO_REG-Savings Loc Natural)
11. Guarda la cuenta y confirma el diálogo
12. Captura y muestra el número de cuenta creado

## Output

El script imprime el número de cuenta creado por consola:

```
============================================================
  CUENTA CREADA EXITOSAMENTE
  Número de cuenta: 2420000731
============================================================
```

## Evidencia

Los screenshots se guardan en `fase2/evidencia/screenshots/` (excluidos del repo vía .gitignore).
