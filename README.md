# SPC libre — Cartas X̄-R y capacidad

Aplicación Shiny para Python que reproduce la lógica de Minitab en el ejercicio 6.34:

- carta X̄-R inicial con todos los subgrupos;
- exclusión manual o automática de causas especiales;
- recálculo de límites sin los subgrupos excluidos;
- conservación de los puntos excluidos en la carta revisada;
- índices Cp, Cpk, Pp y Ppk;
- carga de CSV o Excel;
- exportación de resultados a Excel.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows
pip install -r requirements.txt
shiny run --reload app.py
```

Abra la dirección local que muestre la terminal, normalmente `http://127.0.0.1:8000`.

## Formato de datos

Una fila por subgrupo:

```text
Subgrupo,x1,x2,x3,x4
1,459,449,435,450
2,443,440,442,442
```

Se admiten entre 2 y 10 mediciones por subgrupo.

## Publicar en Posit Connect Cloud

1. Cree un repositorio público en GitHub.
2. Suba a la raíz del repositorio:
   - `app.py`
   - `requirements.txt`
   - `sample_data.csv`
   - `styles.css`
3. Ingrese a Posit Connect Cloud.
4. Pulse **Publish**.
5. Instale o autorice la aplicación de GitHub de Posit Connect Cloud.
6. Seleccione **Shiny for Python**.
7. Elija el repositorio y la rama.
8. Seleccione `app.py` como archivo principal si el asistente lo solicita.
9. Pulse **Publish**.

Las actualizaciones pueden publicarse nuevamente después de hacer `git push`. Si activa la publicación automática, cada cambio en la rama configurada generará una nueva versión.
