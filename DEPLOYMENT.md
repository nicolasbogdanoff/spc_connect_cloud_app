# Publicación en Posit Connect Cloud

La aplicación está construida con **Shiny para Python**. Para publicarla, Posit Connect Cloud necesita que `app.py`, `requirements.txt` y los archivos auxiliares estén en un repositorio de GitHub.

## 1. Probarla localmente (recomendado)

Abra una terminal dentro de la carpeta del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
shiny run --reload app.py
```

En Windows, la activación es:

```powershell
.venv\Scripts\activate
```

La terminal mostrará una dirección local, normalmente:

```text
http://127.0.0.1:8000
```

## 2. Crear el repositorio de GitHub

Cree un repositorio nuevo. Para la modalidad gratuita, lo más sencillo es utilizar un repositorio público.

Suba a la **raíz** del repositorio estos archivos:

```text
app.py
requirements.txt
sample_data.csv
styles.css
README.md
DEPLOYMENT.md
.gitignore
```

### Mediante la web de GitHub

1. Abra el repositorio.
2. Seleccione **Add file → Upload files**.
3. Arrastre todos los archivos anteriores.
4. Confirme con **Commit changes**.

### Mediante Git

```bash
git init
git add .
git commit -m "Aplicación SPC Xbar-R"
git branch -M main
git remote add origin URL_DE_SU_REPOSITORIO
git push -u origin main
```

## 3. Conectar GitHub con Posit Connect Cloud

1. Ingrese a Posit Connect Cloud.
2. Pulse **Publish**, en la esquina superior derecha.
3. La primera vez, autorice la instalación de la aplicación de GitHub de Posit.
4. Conceda acceso al repositorio de la aplicación.
5. Seleccione **Shiny for Python** como framework.
6. Seleccione el repositorio y la rama `main`.
7. Cuando solicite el archivo principal, elija `app.py`.
8. Confirme la publicación.

Connect Cloud leerá `requirements.txt`, instalará las dependencias y ejecutará la aplicación.

## 4. Actualizar la aplicación

Edite los archivos, confirme los cambios y vuelva a enviarlos a GitHub:

```bash
git add .
git commit -m "Actualización de la aplicación"
git push
```

Luego vuelva a publicar desde Connect Cloud o active la publicación automática asociada a la rama del repositorio.

## 5. Errores frecuentes

### La construcción falla al instalar paquetes

Compruebe que cada dependencia esté en una línea separada de `requirements.txt`. No agregue instrucciones `pip install` dentro de `app.py`.

### No encuentra `sample_data.csv` o `styles.css`

Los archivos deben estar en la misma carpeta que `app.py` y conservar exactamente sus nombres.

### La aplicación abre, pero el archivo Excel no funciona

Confirme que `openpyxl` permanezca en `requirements.txt`.

### El gráfico no coincide con Minitab

Para el ejemplo 6.34:

- modo de exclusión: **Manual**;
- subgrupos excluidos: `18`;
- LSL: `420`;
- objetivo: `450`;
- USL: `480`.

La carta revisada debe conservar el punto 18 visible, aunque no participe en el cálculo de los límites.
