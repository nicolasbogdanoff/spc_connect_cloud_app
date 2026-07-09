from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui
from shiny.types import FileInfo


APP_DIR = Path(__file__).parent
SAMPLE_FILE = APP_DIR / "sample_data.csv"

# Constantes estándar para cartas X̄-R (n = 2 a 10)
SPC_CONSTANTS = {
    2: {"A2": 1.880, "D3": 0.000, "D4": 3.267, "d2": 1.128},
    3: {"A2": 1.023, "D3": 0.000, "D4": 2.574, "d2": 1.693},
    4: {"A2": 0.729, "D3": 0.000, "D4": 2.282, "d2": 2.059},
    5: {"A2": 0.577, "D3": 0.000, "D4": 2.114, "d2": 2.326},
    6: {"A2": 0.483, "D3": 0.000, "D4": 2.004, "d2": 2.534},
    7: {"A2": 0.419, "D3": 0.076, "D4": 1.924, "d2": 2.704},
    8: {"A2": 0.373, "D3": 0.136, "D4": 1.864, "d2": 2.847},
    9: {"A2": 0.337, "D3": 0.184, "D4": 1.816, "d2": 2.970},
    10: {"A2": 0.308, "D3": 0.223, "D4": 1.777, "d2": 3.078},
}


def read_uploaded_file(file_info: FileInfo) -> pd.DataFrame:
    """Lee CSV o Excel y devuelve un DataFrame."""
    name = file_info["name"].lower()
    path = file_info["datapath"]

    if name.endswith(".csv"):
        # sep=None intenta detectar coma, punto y coma o tabulación.
        return pd.read_csv(path, sep=None, engine="python")
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(path)

    raise ValueError("Formato no admitido. Utilice CSV, XLSX o XLS.")


def normalize_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Normaliza los datos.

    Reglas:
    - La columna 'Subgrupo' se usa como identificador; si no existe, se usa la primera.
    - Las demás columnas totalmente numéricas se toman como mediciones.
    - Se requieren entre 2 y 10 mediciones por subgrupo, sin valores faltantes.
    """
    if raw.empty:
        raise ValueError("El archivo no contiene datos.")

    df = raw.copy()
    df.columns = [str(c).strip() for c in df.columns]

    subgroup_col = "Subgrupo" if "Subgrupo" in df.columns else df.columns[0]
    df = df.rename(columns={subgroup_col: "Subgrupo"})

    # Convertir el identificador a entero cuando sea posible.
    subgroup_numeric = pd.to_numeric(df["Subgrupo"], errors="coerce")
    if subgroup_numeric.isna().any():
        raise ValueError("La columna Subgrupo debe contener identificadores numéricos.")
    df["Subgrupo"] = subgroup_numeric.astype(int)

    if df["Subgrupo"].duplicated().any():
        raise ValueError("Existen identificadores de subgrupo duplicados.")

    measurement_cols: list[str] = []
    for col in df.columns:
        if col == "Subgrupo":
            continue
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().all():
            df[col] = converted.astype(float)
            measurement_cols.append(col)

    n = len(measurement_cols)
    if n < 2 or n > 10:
        raise ValueError(
            "Se requieren entre 2 y 10 columnas numéricas de medición por subgrupo."
        )

    if df[measurement_cols].isna().any().any():
        raise ValueError("No se permiten mediciones faltantes dentro de un subgrupo.")

    # Conserva el orden original porque en SPC el orden temporal importa.
    return df[["Subgrupo", *measurement_cols]].reset_index(drop=True), measurement_cols


def parse_excluded(text: str, valid_subgroups: set[int]) -> list[int]:
    """Interpreta una lista como '18' o '3, 7, 18'."""
    if text is None or not text.strip():
        return []

    values: list[int] = []
    for token in text.replace(";", ",").split(","):
        token = token.strip()
        if not token:
            continue
        try:
            value = int(token)
        except ValueError as exc:
            raise ValueError(
                f"'{token}' no es un número de subgrupo válido."
            ) from exc
        if value not in valid_subgroups:
            raise ValueError(f"El subgrupo {value} no existe en los datos.")
        if value not in values:
            values.append(value)
    return values


def calculate_subgroup_stats(df: pd.DataFrame, measurement_cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    out["Media"] = out[measurement_cols].mean(axis=1)
    out["Rango"] = out[measurement_cols].max(axis=1) - out[measurement_cols].min(axis=1)
    return out


def calculate_limits(stats: pd.DataFrame, n: int) -> dict[str, float]:
    if stats.empty:
        raise ValueError("No quedan subgrupos para estimar los límites.")

    const = SPC_CONSTANTS[n]
    xbarbar = float(stats["Media"].mean())
    rbar = float(stats["Rango"].mean())
    sigma_within = rbar / const["d2"]

    return {
        "Xbar_LCL": xbarbar - const["A2"] * rbar,
        "Xbar_CL": xbarbar,
        "Xbar_UCL": xbarbar + const["A2"] * rbar,
        "R_LCL": const["D3"] * rbar,
        "R_CL": rbar,
        "R_UCL": const["D4"] * rbar,
        "Media_proceso": xbarbar,
        "Rango_medio": rbar,
        "Sigma_within": sigma_within,
    }


def failures(stats: pd.DataFrame, variable: str, lcl: float, ucl: float) -> list[int]:
    mask = (stats[variable] < lcl) | (stats[variable] > ucl)
    return stats.loc[mask, "Subgrupo"].astype(int).tolist()


def perform_analysis(
    raw_df: pd.DataFrame,
    measurement_cols: list[str],
    exclusion_mode: str,
    manual_excluded: str,
    lsl: float,
    target: float,
    usl: float,
) -> dict[str, Any]:
    stats = calculate_subgroup_stats(raw_df, measurement_cols)
    n = len(measurement_cols)

    initial_limits = calculate_limits(stats, n)
    initial_x_fail = failures(
        stats, "Media", initial_limits["Xbar_LCL"], initial_limits["Xbar_UCL"]
    )
    initial_r_fail = failures(
        stats, "Rango", initial_limits["R_LCL"], initial_limits["R_UCL"]
    )

    if exclusion_mode == "auto":
        excluded = sorted(set(initial_x_fail + initial_r_fail))
    else:
        excluded = parse_excluded(manual_excluded, set(stats["Subgrupo"].astype(int)))

    estimation = stats.loc[~stats["Subgrupo"].isin(excluded)].copy()
    revised_limits = calculate_limits(estimation, n)

    revised_x_fail_all = failures(
        stats, "Media", revised_limits["Xbar_LCL"], revised_limits["Xbar_UCL"]
    )
    revised_r_fail_all = failures(
        stats, "Rango", revised_limits["R_LCL"], revised_limits["R_UCL"]
    )

    revised_x_additional = [x for x in revised_x_fail_all if x not in excluded]
    revised_r_additional = [x for x in revised_r_fail_all if x not in excluded]

    if not (lsl < target < usl):
        raise ValueError("Debe cumplirse LSL < objetivo < USL.")

    values = estimation[measurement_cols].to_numpy(dtype=float).ravel()
    sigma_overall = float(values.std(ddof=1))
    mean_process = revised_limits["Media_proceso"]
    sigma_within = revised_limits["Sigma_within"]

    cp = (usl - lsl) / (6 * sigma_within)
    cpl = (mean_process - lsl) / (3 * sigma_within)
    cpu = (usl - mean_process) / (3 * sigma_within)
    cpk = min(cpl, cpu)

    pp = (usl - lsl) / (6 * sigma_overall)
    ppl = (mean_process - lsl) / (3 * sigma_overall)
    ppu = (usl - mean_process) / (3 * sigma_overall)
    ppk = min(ppl, ppu)

    ppm_within = (
        norm.cdf(lsl, loc=mean_process, scale=sigma_within)
        + 1 - norm.cdf(usl, loc=mean_process, scale=sigma_within)
    ) * 1_000_000

    subgroup_table = stats.copy()
    subgroup_table["Usado_en_límites_revisados"] = ~subgroup_table["Subgrupo"].isin(
        excluded
    )
    subgroup_table["Fuera_X̄_revisada"] = subgroup_table["Subgrupo"].isin(
        revised_x_fail_all
    )
    subgroup_table["Fuera_R_revisada"] = subgroup_table["Subgrupo"].isin(
        revised_r_fail_all
    )

    limits_table = pd.DataFrame(
        {
            "Etapa": ["Inicial", "Revisada"],
            "Subgrupos usados": [len(stats), len(estimation)],
            "LCL X̄": [initial_limits["Xbar_LCL"], revised_limits["Xbar_LCL"]],
            "CL X̄": [initial_limits["Xbar_CL"], revised_limits["Xbar_CL"]],
            "UCL X̄": [initial_limits["Xbar_UCL"], revised_limits["Xbar_UCL"]],
            "LCL R": [initial_limits["R_LCL"], revised_limits["R_LCL"]],
            "CL R": [initial_limits["R_CL"], revised_limits["R_CL"]],
            "UCL R": [initial_limits["R_UCL"], revised_limits["R_UCL"]],
        }
    )

    capability_table = pd.DataFrame(
        {
            "Indicador": [
                "Observaciones usadas",
                "Media del proceso",
                "Rango medio",
                "Sigma within",
                "Sigma overall",
                "Cp",
                "CPL",
                "CPU",
                "Cpk",
                "Pp",
                "PPL",
                "PPU",
                "Ppk",
                "PPM esperado (within)",
            ],
            "Valor": [
                len(values),
                mean_process,
                revised_limits["Rango_medio"],
                sigma_within,
                sigma_overall,
                cp,
                cpl,
                cpu,
                cpk,
                pp,
                ppl,
                ppu,
                ppk,
                ppm_within,
            ],
        }
    )

    stable_revised = not revised_x_additional and not revised_r_additional

    return {
        "stats": stats,
        "estimation": estimation,
        "values": values,
        "measurement_cols": measurement_cols,
        "n": n,
        "excluded": excluded,
        "initial_limits": initial_limits,
        "revised_limits": revised_limits,
        "initial_x_fail": initial_x_fail,
        "initial_r_fail": initial_r_fail,
        "revised_x_fail_all": revised_x_fail_all,
        "revised_r_fail_all": revised_r_fail_all,
        "revised_x_additional": revised_x_additional,
        "revised_r_additional": revised_r_additional,
        "stable_revised": stable_revised,
        "mean": mean_process,
        "sigma_within": sigma_within,
        "sigma_overall": sigma_overall,
        "cp": cp,
        "cpk": cpk,
        "pp": pp,
        "ppk": ppk,
        "lsl": lsl,
        "target": target,
        "usl": usl,
        "subgroup_table": subgroup_table,
        "limits_table": limits_table,
        "capability_table": capability_table,
    }


def control_chart_figure(
    analysis: dict[str, Any], stage: str
) -> plt.Figure:
    """Dibuja carta X̄-R inicial o revisada."""
    stats = analysis["stats"]
    limits = analysis[f"{stage}_limits"]
    excluded = analysis["excluded"] if stage == "revised" else []

    x = np.arange(1, len(stats) + 1)
    labels = stats["Subgrupo"].astype(str).tolist()

    fig, (ax_x, ax_r) = plt.subplots(2, 1, figsize=(12.5, 8.5), sharex=True)

    title = (
        "Carta X̄-R inicial — límites estimados con todos los subgrupos"
        if stage == "initial"
        else "Carta X̄-R revisada — excluidos del cálculo, pero visibles en la carta"
    )
    fig.suptitle(title, fontsize=15, fontweight="bold")

    # Carta X̄
    ax_x.plot(x, stats["Media"], marker="o", linewidth=1.6, label="Media")
    ax_x.axhline(limits["Xbar_UCL"], color="firebrick", linestyle="--", label=f'UCL = {limits["Xbar_UCL"]:.3f}')
    ax_x.axhline(limits["Xbar_CL"], color="seagreen", label=f'CL = {limits["Xbar_CL"]:.3f}')
    ax_x.axhline(limits["Xbar_LCL"], color="firebrick", linestyle="--", label=f'LCL = {limits["Xbar_LCL"]:.3f}')

    x_fail = failures(stats, "Media", limits["Xbar_LCL"], limits["Xbar_UCL"])
    fail_mask = stats["Subgrupo"].isin(x_fail)
    if fail_mask.any():
        ax_x.scatter(x[fail_mask], stats.loc[fail_mask, "Media"], color="crimson", marker="X", s=130, zorder=5, label="Prueba 1")
        for pos, (_, row) in zip(x[fail_mask], stats.loc[fail_mask].iterrows()):
            sg = int(row["Subgrupo"])
            suffix = "\nExcluido del cálculo" if sg in excluded else ""
            ax_x.annotate(
                f"Subgrupo {sg}{suffix}",
                xy=(pos, row["Media"]),
                xytext=(-75, -50),
                textcoords="offset points",
                arrowprops={"arrowstyle": "->"},
                fontsize=8.5,
                fontweight="bold",
            )

    # Marcar excluidos que no estén fuera de límites
    for sg in excluded:
        row_idx = stats.index[stats["Subgrupo"] == sg]
        if len(row_idx) == 0 or sg in x_fail:
            continue
        idx = row_idx[0]
        ax_x.scatter(x[idx], stats.loc[idx, "Media"], facecolors="none", edgecolors="darkorange", s=120, linewidths=2, zorder=5)

    ax_x.set_ylabel("Media del subgrupo")
    ax_x.set_title("Carta X̄")
    ax_x.grid(alpha=0.22)
    ax_x.legend(loc="best", fontsize=8)

    # Carta R
    ax_r.plot(x, stats["Rango"], marker="o", linewidth=1.6, label="Rango")
    ax_r.axhline(limits["R_UCL"], color="firebrick", linestyle="--", label=f'UCL = {limits["R_UCL"]:.3f}')
    ax_r.axhline(limits["R_CL"], color="seagreen", label=f'CL = {limits["R_CL"]:.3f}')
    ax_r.axhline(limits["R_LCL"], color="firebrick", linestyle="--", label=f'LCL = {limits["R_LCL"]:.3f}')

    r_fail = failures(stats, "Rango", limits["R_LCL"], limits["R_UCL"])
    r_mask = stats["Subgrupo"].isin(r_fail)
    if r_mask.any():
        ax_r.scatter(x[r_mask], stats.loc[r_mask, "Rango"], color="crimson", marker="X", s=130, zorder=5, label="Prueba 1")

    for sg in excluded:
        row_idx = stats.index[stats["Subgrupo"] == sg]
        if len(row_idx) == 0:
            continue
        idx = row_idx[0]
        ax_r.scatter(x[idx], stats.loc[idx, "Rango"], facecolors="none", edgecolors="darkorange", s=120, linewidths=2, zorder=5)

    ax_r.set_ylabel("Rango")
    ax_r.set_xlabel("Subgrupo")
    ax_r.set_title("Carta R")
    ax_r.set_xticks(x)
    ax_r.set_xticklabels(labels)
    ax_r.set_xlim(0.5, len(stats) + 0.5)
    ax_r.grid(alpha=0.22)
    ax_r.legend(loc="best", fontsize=8)

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return fig


def capability_figure(analysis: dict[str, Any]) -> plt.Figure:
    values = analysis["values"]
    mean = analysis["mean"]
    sigma_within = analysis["sigma_within"]
    sigma_overall = analysis["sigma_overall"]
    lsl = analysis["lsl"]
    target = analysis["target"]
    usl = analysis["usl"]

    x_min = min(values.min(), lsl) - 5
    x_max = max(values.max(), usl) + 5
    grid = np.linspace(x_min, x_max, 600)

    fig, ax = plt.subplots(figsize=(11.5, 6.5))
    ax.hist(values, bins="auto", density=True, alpha=0.42, edgecolor="black", label="Datos válidos")
    ax.plot(grid, norm.pdf(grid, mean, sigma_within), linewidth=2, label=f"Normal within (σ={sigma_within:.3f})")
    ax.plot(grid, norm.pdf(grid, mean, sigma_overall), linewidth=2, linestyle="--", label=f"Normal overall (s={sigma_overall:.3f})")
    ax.axvline(lsl, color="firebrick", linestyle="--", linewidth=2, label=f"LSL={lsl:g}")
    ax.axvline(target, color="seagreen", linewidth=1.8, label=f"Objetivo={target:g}")
    ax.axvline(usl, color="firebrick", linestyle="--", linewidth=2, label=f"USL={usl:g}")

    summary = (
        f"Media = {mean:.3f}\n"
        f"Cp = {analysis['cp']:.3f}\n"
        f"Cpk = {analysis['cpk']:.3f}\n"
        f"Pp = {analysis['pp']:.3f}\n"
        f"Ppk = {analysis['ppk']:.3f}"
    )
    ax.text(
        0.98,
        0.95,
        summary,
        transform=ax.transAxes,
        ha="right",
        va="top",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.9},
    )

    ax.set_title("Capacidad del proceso — distribución normal")
    ax.set_xlabel("Medición")
    ax.set_ylabel("Densidad")
    ax.grid(alpha=0.18)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    return fig


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Datos"),
        ui.input_radio_buttons(
            "source",
            "Fuente",
            {"sample": "Ejemplo 6.34 incluido", "upload": "Subir archivo"},
            selected="sample",
        ),
        ui.input_file(
            "file",
            "CSV o Excel",
            accept=[".csv", ".xlsx", ".xls"],
            multiple=False,
        ),
        ui.hr(),
        ui.h4("Exclusión de causas especiales"),
        ui.input_radio_buttons(
            "exclusion_mode",
            "Modo",
            {
                "manual": "Manual",
                "auto": "Automática: puntos fuera de 3σ en la carta inicial",
            },
            selected="manual",
        ),
        ui.input_text("excluded", "Subgrupos excluidos", value="18"),
        ui.help_text(
            "Los subgrupos excluidos no estiman los límites revisados, pero siguen visibles en la carta, igual que en Minitab."
        ),
        ui.hr(),
        ui.h4("Especificaciones"),
        ui.input_numeric("lsl", "LSL", 420),
        ui.input_numeric("target", "Objetivo", 450),
        ui.input_numeric("usl", "USL", 480),
        ui.hr(),
        ui.download_button("download_results", "Descargar resultados Excel", width="100%"),
        ui.download_button("download_sample", "Descargar datos de ejemplo", width="100%"),
        width=330,
        open="desktop",
    ),
    ui.tags.head(ui.tags.link(rel="stylesheet", href="styles.css")),
    ui.layout_columns(
        ui.value_box("Estado revisado", ui.output_text("status_value"), theme="primary"),
        ui.value_box("Media", ui.output_text("mean_value"), theme="light"),
        ui.value_box("σ within", ui.output_text("sigma_value"), theme="light"),
        ui.value_box("Cpk", ui.output_text("cpk_value"), theme="light"),
        col_widths=(3, 3, 3, 3),
        fill=False,
    ),
    ui.navset_card_tab(
        ui.nav_panel(
            "Cartas de control",
            ui.card(
                ui.card_header("Carta inicial"),
                ui.output_plot("initial_chart", height="720px"),
                full_screen=True,
            ),
            ui.card(
                ui.card_header("Carta revisada: punto excluido visible"),
                ui.output_plot("revised_chart", height="720px"),
                full_screen=True,
            ),
        ),
        ui.nav_panel(
            "Capacidad",
            ui.card(
                ui.output_plot("capability_chart", height="600px"),
                full_screen=True,
            ),
            ui.card(
                ui.card_header("Índices de capacidad"),
                ui.output_data_frame("capability_table"),
            ),
        ),
        ui.nav_panel(
            "Resultados numéricos",
            ui.card(
                ui.card_header("Pruebas de control"),
                ui.output_text_verbatim("test_results"),
            ),
            ui.card(
                ui.card_header("Límites"),
                ui.output_data_frame("limits_table"),
            ),
            ui.card(
                ui.card_header("Estadísticos por subgrupo"),
                ui.output_data_frame("subgroup_table"),
            ),
        ),
        ui.nav_panel(
            "Ayuda",
            ui.markdown(
                """
### Cómo reproduce la lógica de Minitab

1. La **carta inicial** usa todos los subgrupos para estimar la línea central y los límites.
2. Los subgrupos indicados como causas especiales se retiran **solo del conjunto de estimación**.
3. La **carta revisada** vuelve a mostrar todos los puntos, incluidos los excluidos.
4. Los límites revisados se calculan únicamente con los subgrupos aceptados.
5. Por eso el punto 18 puede seguir visible y fuera de control, aunque no intervenga en los nuevos límites.

### Formato del archivo

- Una fila por subgrupo.
- Primera columna: `Subgrupo`.
- Entre 2 y 10 columnas numéricas de medición, por ejemplo `x1`, `x2`, `x3`, `x4`.
- Sin celdas vacías dentro de un subgrupo.

### Precaución metodológica

La exclusión de un punto debe justificarse mediante una **causa asignable**. La opción automática sirve como ayuda diagnóstica, no como autorización para eliminar observaciones sin investigación del proceso.
                """
            ),
        ),
        id="main_tabs",
    ),
    title="SPC libre — Cartas X̄-R y capacidad",
    fillable=True,
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    def raw_data() -> tuple[pd.DataFrame, list[str]]:
        if input.source() == "sample":
            raw = pd.read_csv(SAMPLE_FILE)
        else:
            upload: list[FileInfo] | None = input.file()
            req(upload is not None)
            raw = read_uploaded_file(upload[0])
        return normalize_data(raw)

    @reactive.calc
    def analysis() -> dict[str, Any]:
        df, measurement_cols = raw_data()
        return perform_analysis(
            raw_df=df,
            measurement_cols=measurement_cols,
            exclusion_mode=input.exclusion_mode(),
            manual_excluded=input.excluded(),
            lsl=float(input.lsl()),
            target=float(input.target()),
            usl=float(input.usl()),
        )

    @render.text
    def status_value():
        a = analysis()
        return "Estable" if a["stable_revised"] else "Revisar señales"

    @render.text
    def mean_value():
        return f"{analysis()['mean']:.3f}"

    @render.text
    def sigma_value():
        return f"{analysis()['sigma_within']:.3f}"

    @render.text
    def cpk_value():
        return f"{analysis()['cpk']:.3f}"

    @render.plot(alt="Carta X barra y R inicial")
    def initial_chart():
        return control_chart_figure(analysis(), "initial")

    @render.plot(alt="Carta X barra y R revisada")
    def revised_chart():
        return control_chart_figure(analysis(), "revised")

    @render.plot(alt="Gráfico de capacidad del proceso")
    def capability_chart():
        return capability_figure(analysis())

    @render.data_frame
    def limits_table():
        return render.DataTable(
            analysis()["limits_table"].round(4),
            width="100%",
            height="220px",
            filters=False,
        )

    @render.data_frame
    def subgroup_table():
        return render.DataTable(
            analysis()["subgroup_table"].round(4),
            width="100%",
            height="520px",
            filters=True,
        )

    @render.data_frame
    def capability_table():
        return render.DataTable(
            analysis()["capability_table"].round(4),
            width="100%",
            height="480px",
            filters=False,
        )

    @render.text
    def test_results():
        a = analysis()
        excluded = a["excluded"] or "ninguno"
        return (
            f"Carta inicial X̄ — prueba 1: {a['initial_x_fail'] or 'ninguno'}\n"
            f"Carta inicial R  — prueba 1: {a['initial_r_fail'] or 'ninguno'}\n\n"
            f"Subgrupos excluidos de la estimación revisada: {excluded}\n"
            f"Carta revisada X̄ — todos los puntos visibles fuera de límite: {a['revised_x_fail_all'] or 'ninguno'}\n"
            f"Carta revisada R  — todos los puntos visibles fuera de límite: {a['revised_r_fail_all'] or 'ninguno'}\n\n"
            f"Señales adicionales no excluidas en X̄: {a['revised_x_additional'] or 'ninguna'}\n"
            f"Señales adicionales no excluidas en R: {a['revised_r_additional'] or 'ninguna'}"
        )

    @render.download(filename="resultados_spc.xlsx")
    def download_results():
        a = analysis()
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            a["subgroup_table"].to_excel(writer, sheet_name="Subgrupos", index=False)
            a["limits_table"].to_excel(writer, sheet_name="Limites", index=False)
            a["capability_table"].to_excel(writer, sheet_name="Capacidad", index=False)
        yield buffer.getvalue()

    @render.download(filename="datos_ejemplo_6_34.csv", media_type="text/csv")
    def download_sample():
        yield SAMPLE_FILE.read_bytes()


app = App(app_ui, server, static_assets=APP_DIR)
