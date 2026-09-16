# Contribuir a SPC Connect

Gracias por ayudar a mejorar esta herramienta de análisis estadístico para ingeniería.

## Preparar el entorno

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest
```

En Windows PowerShell, activa el entorno con `.venv\\Scripts\\Activate.ps1`.

## Antes de abrir un Pull Request

1. Describe el problema o la decisión de diseño que resuelve el cambio.
2. Añade o actualiza pruebas para cualquier comportamiento calculado.
3. Ejecuta `pytest -q` y comprueba que no haya cambios accidentales.
4. Si cambias la interfaz, incluye una captura o describe el flujo afectado.
5. No incluyas datos reales de procesos, credenciales ni archivos de instalaciones locales.

## Criterios del proyecto

- Mantener visible la trazabilidad entre datos, exclusiones, límites y resultados.
- No eliminar observaciones automáticamente por estar fuera de control.
- Explicar supuestos estadísticos y limitaciones en la documentación.
- Preferir cambios pequeños, verificables y compatibles con el flujo educativo.

Para cambios grandes, abre primero un issue para acordar el alcance.
