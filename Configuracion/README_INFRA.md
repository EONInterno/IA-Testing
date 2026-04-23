# Infraestructura y Configuración del Entorno

## 1. Flujo de Conexión VPN

El acceso a los sistemas SAP internos de Banco Atlántida requiere una conexión VPN corporativa
a través de Cisco AnyConnect (protocolo `anyconnect`).

**Flujo:**
1. Se ejecuta `Configuracion/connect-bancatlan.sh`.
2. El script lee las credenciales desde variables de entorno (`BANCATLAN_VPN_USER`, `BANCATLAN_VPN_PASSWORD`).
   Si no están definidas, las solicita interactivamente.
3. `openconnect` establece la conexión al host `vpn.bancatlan.hn` usando el protocolo AnyConnect.
4. Se utiliza el flag `--useragent="AnyConnect Linux_64 4.10.07061"` para evitar el rechazo
   por versión de cliente ("Please upgrade your AnyConnect Client").
5. Una vez conectado, el túnel VPN permite acceso a la red interna (incluyendo `10.165.6.8` para SAP).

## 2. Nota sobre MFA (Multi-Factor Authentication)

Durante las pruebas iniciales del entorno, **sí se solicitó MFA** y fue aprobado manualmente.
Esto significa que en ejecuciones futuras debemos estar preparados para que el servidor VPN
solicite un segundo factor de autenticación (push notification o código TOTP).

**Implicaciones:**
- El script de VPN está diseñado para pausarse y esperar la aprobación manual del MFA.
- En entornos CI/CD, se necesitará un operador humano disponible para aprobar el MFA,
  o bien gestionar una excepción de MFA con el equipo de seguridad de Banco Atlántida.
- El primer factor (password) se puede automatizar vía variable de entorno;
  el segundo factor requiere intervención humana.

## 3. Política: No Automatizar el MFA

**REGLA ESTRICTA:** El MFA NO debe ser automatizado de forma programática.

Razones:
- Automatizar el MFA viola las políticas de seguridad corporativas.
- Los tokens TOTP o push notifications son mecanismos de seguridad diseñados
  para requerir presencia humana.
- Cualquier intento de bypass del MFA podría resultar en bloqueo de cuentas
  o escalamiento con el equipo de seguridad.

**Procedimiento correcto:**
1. Ejecutar el script de VPN.
2. Cuando aparezca el prompt de MFA, un operador humano debe aprobar manualmente.
3. Una vez establecida la VPN, las pruebas automatizadas de Playwright pueden ejecutarse
   sin intervención adicional.

## 4. Certificado CA (host 10.165.6.8)

El servidor SAP en `10.165.6.8` utiliza un certificado autofirmado o de CA interna.
Para que Playwright y las herramientas del entorno confíen en él:

- Ejecutar `Configuracion/setup-ca-trust.sh` para descargar e instalar el certificado
  en el trust store del sistema.
- Configurar `NODE_EXTRA_CA_CERTS` para Node.js/Playwright.
- Como fallback, `playwright.config.js` tiene `ignoreHTTPSErrors: true`.

## 5. Dependencias del Entorno

| Herramienta     | Propósito                                    |
|-----------------|----------------------------------------------|
| `openconnect`   | Cliente VPN compatible con Cisco AnyConnect  |
| `curl`          | Verificación de conectividad                 |
| `openssl`       | Descarga de certificados CA                  |
| Node.js 18+     | Runtime para Playwright (JS/TS)              |
| Python 3.9+     | Runtime para scripts de automatización SAP   |
| Playwright      | Motor de automatización de navegador         |
