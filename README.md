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


