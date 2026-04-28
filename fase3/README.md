# Fase 3 — Creación de Contrato de Préstamo

Script para automatizar la creación de contratos de préstamo en SAP Fiori.

## Requisitos

- Python 3.9+
- Playwright (`pip install playwright && python -m playwright install chromium`)
- Chrome corriendo con CDP en `localhost:29229`
- VPN conectada a la red SAP
- Sesión SAP activa o credenciales en variables de entorno (`SAP_USER`, `SAP_PASSWORD`)

## Parámetros (dinámicos, solicitados por consola)

| Parámetro | Ejemplo |
|---|---|
| ID_CLIENTE | 1000430 |
| FECHA_INICIO | 24/10/2005 |
| PRODUCTO | Personal Loan C4B |
| MONTO | 10000 |
| DURACION | 3 |
| DURACION_UNIDAD | Months |
| FIXING_TYPE | Fixed Interest |
| FRECUENCIA | Weekly |
| KEY_DATE | Anniversary Date |
| TASA_INTERES | 7 |
| SALES_PRODUCT | Local CDP Consumer Loan |
| INCOME | Personal Loan |
| FECI_INDICATOR | Interests Discount |
| PREFERENTIAL_INDICATOR | Preferential |
| LOAN_CLASSIFICATION | Mención Especial |
| CINU_ACTIVITY_TYPE | Préstamo Personal |
| REGION_CODE | PANAMA |
| CUENTA_DEBITO | 2420000731 |

## Ejecución

```bash
python fase3/crear_contrato.py
```

## Flujo de navegación

1. Shell Home → "More groups" → "Loan Accounts"
2. Click "Loan Contract - Create"
3. Buscar cliente por Customer No
4. Click "Create" → Seleccionar fecha → "Continue"
5. Seleccionar Manager (primera opción)
6. Seleccionar Producto de préstamo
7. Llenar 6 secciones del formulario:
   - 1. Contract (monto, duración, fixing type)
   - 2. Settlement (frecuencia, key date)
   - 3. Conditions (tasa de interés nominal)
   - 4. Parties Roles (omitida)
   - 5. Additional Loan Details (sales product, income, FECI, etc.)
   - 6. Payment Party (región, cuenta débito/desembolso)
8. Click "Calculate" → Esperar simulación
9. Click "CREATE LOAN" → Capturar Loan Contract ID

## Output

El script imprime el ID del contrato creado por consola:
```
[OUTPUT] Loan Contract ID: XXXXXXXXXX
```
