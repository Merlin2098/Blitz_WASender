# ADR 0001: Incidente por cambio de DOM en WhatsApp Web

## Estado

Aprobado

## Fecha

2026-03-25

## Contexto

La aplicación dejó de funcionar después de un cambio en la interfaz de WhatsApp Web.

El síntoma principal fue un falso negativo durante la carga inicial:

- la app mostraba `WhatsApp Web no cargó. ¿Escaneaste el código QR?`
- sin embargo, el perfil aislado de Selenium sí tenía sesión activa
- el diagnóstico HTML mostró que la bandeja principal ya estaba visible

La implementación original dependía de selectores frágiles, especialmente:

- `//div[@contenteditable='true'][@data-tab='3']` para detectar sesión cargada
- `//div[@contenteditable='true'][@data-tab='10']` para escribir el mensaje

El diagnóstico realizado con scripts de mantenimiento mostró que el DOM actual cambió de forma relevante:

- la búsqueda principal ya no se expone de forma confiable como `div[contenteditable]`
- en la vista inicial existe un `input` con `role="textbox"` y `aria-label` de búsqueda
- la bandeja lateral `#pane-side` es una señal más estable de que WhatsApp Web ya cargó
- en un chat abierto, el compositor real sigue exponiéndose como un nodo con `role="textbox"` y `aria-label` tipo `Escribir un mensaje ...`
- el botón de envío se expone con `aria-label="Enviar"` y se puede usar como fallback

## Decisión

Se decide:

1. Reemplazar la detección rígida de carga por selectores más tolerantes a cambios de DOM.
2. Priorizar señales estructurales de la app cargada, especialmente `#pane-side`, búsqueda visible y controles de sesión.
3. Mantener el flujo principal de apertura por URL directa a chat, pero desacoplar:
   - detección de sesión activa
   - detección de chat abierto
   - detección del compositor de mensaje
4. Mantener `Enter` como mecanismo primario de envío y usar el botón `Enviar` solo como fallback explícito.
5. Crear scripts de mantenimiento bajo `scripts/` para diagnóstico manual y reproducción controlada del perfil aislado usado por Selenium.

## Scripts de mantenimiento

Los siguientes scripts quedan como soporte operativo:

- [scripts/launch_edge_recording_profile.py](../../scripts/launch_edge_recording_profile.py)
  - abre Microsoft Edge con el perfil aislado `perfiles/edge`
  - permite inspección manual o uso de herramientas de grabación

- [scripts/record_whatsapp_manual_session.py](../../scripts/record_whatsapp_manual_session.py)
  - abre Edge con el perfil aislado
  - se adjunta por depuración remota
  - registra eventos manuales, HTML y screenshots para diagnóstico

## Consecuencias

### Positivas

- la aplicación vuelve a detectar correctamente cuando WhatsApp Web ya cargó
- se reduce la dependencia de un único selector inestable
- los incidentes futuros sobre cambios de DOM se pueden diagnosticar más rápido
- el perfil aislado de Selenium queda tratable como activo de mantenimiento y no como caja negra

### Negativas

- la automatización sigue dependiendo de un DOM no oficial y cambiante
- cualquier cambio profundo de WhatsApp Web puede volver a romper selectores
- se introduce una pequeña superficie adicional de mantenimiento en `scripts/`

## Evidencia del incidente

La investigación se apoyó en:

- logs de ejecución de la GUI
- capturas diagnósticas de `logs/whatsapp_diagnostics/`
- grabaciones manuales de `logs/manual_action_recordings/`

La evidencia más importante fue:

- la página cargaba con `title` tipo `WhatsApp`
- `#pane-side` estaba presente
- los selectores legacy devolvían `0`
- el compositor real del chat se detectó por `role="textbox"` y `aria-label`

## Resultado

El incidente quedó mitigado ajustando `utils/whatsapp_sender.py` para:

- detectar mejor la carga inicial
- abrir y validar el chat con selectores más robustos
- enviar por `Enter` con fallback controlado al botón `Enviar`
