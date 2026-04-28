# Estrategia de Testing Periódico Automatizado

**Objetivo:** Ejecutar periódicamente los scripts de las 3 fases, detectar errores, corregirlos y generar reportes de resultados.

---

## 1. Arquitectura Propuesta

```
┌─────────────────────────────────────────────────┐
│  Devin (Sesión Programada)                      │
│                                                 │
│  1. Conectar VPN (fase1/vpn_connect.py)         │
│  2. Login SAP (fase1/sap_login.py)              │
│  3. Crear Cuenta de Ahorro (fase2/)             │
│  4. Crear Contrato de Préstamo (fase3/)         │
│  5. Validar resultados                          │
│  6. Generar reporte                             │
│  7. Si hay errores → diagnosticar y corregir    │
│  8. Re-ejecutar tests corregidos                │
│  9. Commit fixes + Notificar al usuario         │
└─────────────────────────────────────────────────┘
```

---

## 2. Configuración con Devin Scheduled Sessions

Devin soporta **sesiones programadas** que ejecutan un playbook automáticamente en un horario definido.

### 2.1 Crear un Playbook de Testing

Se debe crear un playbook en Devin con las instrucciones para ejecutar el ciclo completo de testing:

**Nombre:** `SAP Fiori - Testing Periódico Fases 1-2-3`

**Instrucciones del Playbook:**
```
Ejecutar el ciclo completo de testing SAP Fiori:

1. SETUP:
   - Clonar el repositorio EONInterno/IA-Testing (branch: devin/1777063348-fase1-vpn-sap-login)
   - Solicitar credenciales VPN via secrets (VPN_USER, VPN_PASSWORD)
   - Instalar dependencias: pip install -r fase1/requirements.txt

2. FASE 1 - VPN + Login:
   - Ejecutar fase1/main.py con las credenciales proporcionadas
   - Verificar: VPN conectada + SAP Shell Home accesible
   - Si falla VPN: reportar error de red, no continuar

3. FASE 2 - Cuenta de Ahorro:
   - Ejecutar fase2/crear_cuenta_ahorro.py
   - Parámetros de prueba:
     ID_CLIENTE: 1000430
     FECHA_INICIO: (fecha del día de ejecución)
     PRODUCTO: Cuenta De Ahorro Pacific Bank
     CONDICION_GRUPO: Test Automatizado Devin
   - Verificar: número de cuenta retornado (no "ERROR" ni "NO_CAPTURADO")

4. FASE 3 - Contrato de Préstamo:
   - Ejecutar fase3/crear_contrato.py
   - Parámetros de prueba:
     ID_CLIENTE: 1000430
     FECHA_INICIO: (fecha del día de ejecución)
     PRODUCTO: Personal Loan C4B
     MONTO: 10000
     DURACION: 3
     DURACION_UNIDAD: Months
     FIXING_TYPE: Fixed Interest
     FRECUENCIA: Weekly
     KEY_DATE: Anniversary Date
     TASA_INTERES: 7
     SALES_PRODUCT: Local CDP Consumer Loan
     INCOME: Personal Loan
     FECI_INDICATOR: Interests Discount
     PREFERENTIAL_INDICATOR: Preferential
     LOAN_CLASSIFICATION: Mención Especial
     CINU_ACTIVITY_TYPE: Préstamo Personal
     REGION_CODE: PANAMA
     CUENTA_DEBITO: (usar la cuenta creada en Fase 2)
   - Verificar: Loan Contract ID retornado

5. DETECCIÓN Y CORRECCIÓN DE ERRORES:
   - Si alguna fase falla, analizar el error:
     a) Error de selector SAP → SAP cambió la UI → actualizar selectores
     b) Error de timeout → aumentar tiempos de espera
     c) Error de VPN → reportar problema de red
     d) Error de credenciales → notificar al usuario
   - Aplicar la corrección al código
   - Re-ejecutar la fase fallida
   - Si la corrección funciona, hacer commit y push

6. REPORTE:
   - Generar archivo TESTING_RESULTS_[fecha].md con:
     - Fecha y hora de ejecución
     - Resultado de cada fase (PASS/FAIL)
     - Errores encontrados y correcciones aplicadas
     - IDs de cuentas/contratos creados
     - Tiempo total de ejecución
   - Enviar notificación al usuario con resumen
```

### 2.2 Configurar el Schedule

En la interfaz de Devin (https://app.devin.ai):

1. Ir a **Playbooks** → Crear el playbook con las instrucciones anteriores
2. Ir a **Schedules** → Crear nuevo schedule:
   - **Playbook:** SAP Fiori - Testing Periódico
   - **Frecuencia recomendada:** Semanal (cada lunes a las 9:00 AM hora local)
   - **Repositorio:** EONInterno/IA-Testing
3. Configurar **secrets necesarios:**
   - `VPN_USER` y `VPN_PASSWORD` → Devin los solicitará cada ejecución
   - `SAP_PASSWORD` → Puede ser un secret permanente de organización

---

## 3. Formato del Reporte de Resultados

Cada ejecución genera un reporte con este formato:

```markdown
# Reporte de Testing — [Fecha]

## Resumen
| Fase | Estado | Duración |
|------|--------|----------|
| 1 - VPN + Login | PASS | 45s |
| 2 - Cuenta de Ahorro | PASS | 120s |
| 3 - Contrato Préstamo | FAIL → FIXED | 180s |

## Detalle de Errores
### Fase 3 - Error en selector de Region Code
- **Error:** `TimeoutError: Locator [id*='RegionCode'] no encontrado`
- **Causa:** SAP actualizó el ID del elemento a `[id*='regionCodeSelect']`
- **Corrección:** Actualizado patrón de búsqueda en `_seleccionar_dropdown()`
- **Re-test:** PASS

## Artefactos Creados
- Cuenta de Ahorro: 2420000732
- Contrato de Préstamo: LP-2026-00045

## Correcciones Commiteadas
- Commit: abc1234 — "fix: actualizar selector Region Code en fase3"
```

---

## 4. Flujo de Detección y Corrección Autónoma

```
Script falla
    │
    ▼
Analizar tipo de error
    │
    ├── Timeout/Selector ──► Inspeccionar DOM actual
    │                        ► Encontrar nuevo selector
    │                        ► Actualizar código
    │                        ► Re-ejecutar
    │
    ├── Error de red/VPN ──► Reintentar conexión (max 3)
    │                        ► Si persiste → reportar al usuario
    │
    ├── Error SAP (diálogo) ► Capturar screenshot
    │                        ► Intentar cerrar/aceptar diálogo
    │                        ► Re-ejecutar paso
    │
    └── Error desconocido ──► Capturar screenshot + logs
                              ► Reportar al usuario sin modificar código
```

---

## 5. Opciones de Frecuencia

| Frecuencia | Caso de Uso | Costo Estimado |
|---|---|---|
| **Diaria** | Entornos con cambios frecuentes en SAP | ~30 min ACUs/día |
| **Semanal** (recomendado) | Entornos estables, detección temprana | ~30 min ACUs/semana |
| **Quincenal** | Entornos muy estables | ~30 min ACUs/2 semanas |
| **Manual (bajo demanda)** | Cuando se necesite | Solo cuando se ejecute |

**Recomendación:** Empezar con frecuencia **semanal** y ajustar según la tasa de errores encontrados. Si durante 4 semanas consecutivas no hay errores, reducir a quincenal. Si se detectan errores en 2 de 4 semanas, aumentar a diaria.

---

## 6. Pasos para Activar

1. **Guardar credenciales SAP como secret permanente** (ya configurado como `SAP_PASSWORD`)
2. **Crear el playbook** en https://app.devin.ai con las instrucciones de la sección 2.1
3. **Crear el schedule** con la frecuencia deseada
4. **Primera ejecución manual** para validar que el playbook funcione correctamente
5. **Revisar el primer reporte** y ajustar parámetros si es necesario

Las credenciales VPN (`VPN_USER`, `VPN_PASSWORD`) se solicitarán como secrets temporales en cada ejecución, ya que cambian periódicamente.
