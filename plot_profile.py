#!/usr/bin/env python3
"""
Plot stacked bar charts from perf_profile JSON output.

- Cada barra = um workload
- Segmentos = Branch, FP, INT_rest, Load, Store
- Mostra a composição percentual das instruções
- Cada categoria tem cor + textura (hatch) para melhor visualização
"""

import json
import argparse
import matplotlib
matplotlib.use("Agg") # Backend padrão para PDF
import matplotlib.pyplot as plt
import pandas as pd
import os

def load_json_files(file_list):
    """Carrega múltiplos JSONs em uma lista de dicionários"""
    data_list = []
    for f in file_list:
        with open(f, 'r') as fp:
            data_list.append(json.load(fp))
    return data_list

def prepare_dataframe(data_list):
    """Cria DataFrame para stacked bar: Branch, FP, INT_rest, Load, Store"""
    rows = []
    for d in data_list:
        row = {
            "workload": d["workload_name"],
            "Branches": d["DERIVED"].get("Branches",0),
            "Floating-point": d["DERIVED"].get("FP_total",0),
            "Integer": d["DERIVED"].get("INT_rest",0),
            "Load": d["DERIVED"].get("Load",0),
            "Store": d["DERIVED"].get("Store",0)
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    df.set_index("workload", inplace=True)

    df.index = [name.replace('_', r'\_') for name in df.index]

    # Normaliza para porcentagem
    df_percent = df.div(df.sum(axis=1), axis=0) * 100
    return df_percent

def plot_stacked_bar(df):
    """Plota o stacked bar em porcentagem com grid horizontal e texturas"""
    width_pt = 455.24413
    inches_per_pt = 1.0 / 72.27
    fig_width = width_pt * inches_per_pt
    fig_height = fig_width * 0.5

    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],
        "font.size": 11,             # Ajuste para 10 ou 12 se seu documento mudar
        "axes.labelsize": 11,
        "legend.fontsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "figure.figsize": [fig_width, fig_height],
        "figure.autolayout": True,   # Ajuda a não cortar labels
    })

    fig, ax = plt.subplots()

    colors = {
        "Branches": "#f39c12",
        "Floating-point": "#3498db",
        "Integer": "#2ecc71",
        "Load": "#9b59b6",
        "Store": "#e74c3c"
    }

    hatches = {
        "Branches": "oo",
        "Floating-point": "xx",
        "Integer": "//",
        "Load": "..",
        "Store": "--"
    }


    bottom = pd.Series([0]*len(df), index=df.index)

    for col in df.columns:
        ax.bar(
            df.index, df[col], 
            bottom=bottom, 
            color=colors[col], 
            label=col, 
            hatch=hatches[col]
        )
        bottom += df[col]

    # Grid horizontal pontilhado
    ax.yaxis.grid(True, linestyle=':', linewidth=0.8, alpha=0.7)

    # Eixo Y em porcentagem
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_ylabel("Distrubuição de Instruções (\%)")
    ax.set_xlabel("Workloads")

    # Legenda horizontal acima do gráfico
    ax.legend(
        title="Tipos de Instrução",
        loc='lower center',          # O ponto de ancoragem da legenda é a base dela
        bbox_to_anchor=(0.5, 1.02),  # (X=meio, Y=logo acima do 1.0 que é o topo do eixo)
        ncol=len(df.columns),        # Mantém horizontal
        fontsize=9,
        frameon=False,
        handletextpad=0.4,
        columnspacing=1.0
    )

    plt.tight_layout()

    # Nomes dos workloads em 45°
    plt.xticks(rotation=45, ha='right')

    plt.savefig("workloads.pdf", bbox_inches="tight")

def main():
    parser = argparse.ArgumentParser(description="Plot perf_profile JSON as stacked bar charts")
    parser.add_argument("json_files", nargs="+", help="JSON files from perf_profile.py")
    args = parser.parse_args()

    data_list = load_json_files(args.json_files)
    df = prepare_dataframe(data_list)
    plot_stacked_bar(df)

if __name__ == "__main__":
    main()