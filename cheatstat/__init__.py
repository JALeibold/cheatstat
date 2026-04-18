"""
cheatstat.py – Einfache statistische Funktionen für Datenanalyse mit Survey-Gewichtung

Enthält:
- describe_df(df): Kompakte Übersicht über alle Variablen
- missing_report(df): Fehlende-Werte-Analyse
- recode(df, column, mapping, ...): Variablen umkodieren (mit Bereichen, Operatoren)
- fre(df, column, weight=None): Häufigkeitstabelle mit Gewichtung
- fre_wl(df, column, labels, weight=None): Kombinierte Tabelle mit Gewichtung
- uniV(df, column_name, weight=None, se=False): Einzelvariable Analyse
- biV(df, col1, col2, scale, weight=None): Zweifache Analyse
- cross_tab(df, col1, col2, weight=None, ...): Kreuztabelle
- ttest_u(group, g1, g2, dependent, data, weight=None): Unabhängiger t-Test
- regress(formula, data, weight=None, ...): OLS-Regression mit Beta
- beta(formula, data, weight=None, full=False): Standardisierte β-Koeffizienten
- cronbach(df, items, weight=None): Reliabilitätsanalyse
- effect_size(test_type, **kwargs): Effektstärken-Rechner
- normality_test(df, column): Normalverteilungstests
- compare_groups(df, group, variables, weight=None): Gruppenvergleich
- export_results(result, filename, format='excel'): Ergebnisse exportieren
- create_dummies(df, column, prefix=None): Dummy-Variablen
- help_cheatstat(): Kurzanleitung

Autor: Jürgen Leibold
Version: 4.1
"""

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, chi2, kendalltau, spearmanr, pearsonr
from functools import lru_cache
from scipy import stats
from scipy.stats import levene, ttest_ind
import warnings
import re

# statsmodels
try:
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    warnings.warn(
        "statsmodels nicht installiert. regress() ist nicht verfügbar.\n"
        "Installation: pip install statsmodels"
    )

# numba
try:
    from numba import njit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    def njit(f=None, **kwargs):
        if f is not None:
            return f
        return lambda func: func


# ===============================================================
# Scale-Aliases
# ===============================================================

SCALE_ALIASES = {
    'n': 'n', 'nominal': 'n', 'kategorial': 'n', 'kat': 'n',
    'om': 'om', 'ordinal': 'om', 'metrisch': 'om',
    'ordinal-metrisch': 'om', 'o': 'om', 'm': 'om'
}


# ===============================================================
# StatResult – Einheitlicher Ergebnis-Container
# ===============================================================

class StatResult:
    """
    Einheitlicher Container für statistische Ergebnisse.

    Verwendung:
        result.summary()           → Formatierte Ausgabe
        result.summary(show_tables=True) → inkl. Tabellen
        result['stat']             → Statistik-DataFrame
        result['observed']         → Tabelle per Key
        result.keys()              → Alle verfügbaren Schlüssel
    """

    def __init__(self, tables=None, stat=None, test_name="", info=None):
        self.tables = tables or {}
        self.stat = stat
        self.test_name = test_name
        self.info = info or {}

    def summary(self, show_tables=False):
        print(f"\n{'=' * 60}")
        print(f"  {self.test_name}")
        print(f"{'=' * 60}")

        if self.info:
            for key, val in self.info.items():
                if isinstance(val, float):
                    print(f"  {key}: {val:.4f}")
                else:
                    print(f"  {key}: {val}")
            print(f"{'-' * 60}")

        if self.stat is not None:
            print(self.stat.to_string(index=False))

        if show_tables and self.tables:
            for name, table in self.tables.items():
                print(f"\n--- {name} ---")
                if isinstance(table, pd.DataFrame):
                    print(table.to_string())
                elif isinstance(table, StatResult):
                    table.summary(show_tables=True)
                else:
                    print(table)

        print(f"{'=' * 60}\n")

    def __repr__(self):
        n_tables = len(self.tables)
        has_stat = "mit Statistiken" if self.stat is not None else "ohne Statistiken"
        return f"StatResult('{self.test_name}', {n_tables} Tabellen, {has_stat})"

    def __getitem__(self, key):
        if key == 'stat':
            return self.stat
        if key == 'stats':
            return self.stat
        if key in self.tables:
            return self.tables[key]
        if key in self.info:
            return self.info[key]
        available = ['stat'] + list(self.tables.keys()) + list(self.info.keys())
        raise KeyError(f"Schlüssel '{key}' nicht gefunden. Verfügbar: {available}")

    def keys(self):
        result = []
        if self.stat is not None:
            result.append('stat')
        result.extend(self.tables.keys())
        result.extend(self.info.keys())
        return result


# ===============================================================
# Concordant/Discordant
# ===============================================================

if NUMBA_AVAILABLE:
    @njit
    def _count_concordant_discordant_full_numba(x, y):
        n = len(x)
        C = D = T_x = T_y = 0
        for i in range(n):
            for j in range(i + 1, n):
                dx = x[i] - x[j]
                dy = y[i] - y[j]
                if dx == 0.0 and dy == 0.0:
                    T_x += 1
                    T_y += 1
                elif dx == 0.0:
                    T_x += 1
                elif dy == 0.0:
                    T_y += 1
                elif (dx > 0 and dy > 0) or (dx < 0 and dy < 0):
                    C += 1
                else:
                    D += 1
        return C, D, T_x, T_y

    def _count_concordant_discordant_full(x, y):
        return _count_concordant_discordant_full_numba(
            np.asarray(x, dtype=np.float64),
            np.asarray(y, dtype=np.float64)
        )
else:
    def _count_concordant_discordant_full(x, y):
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        n = len(x)
        C = D = T_x = T_y = 0
        for i in range(n):
            for j in range(i + 1, n):
                dx = x[i] - x[j]
                dy = y[i] - y[j]
                if dx == 0.0 and dy == 0.0:
                    T_x += 1
                    T_y += 1
                elif dx == 0.0:
                    T_x += 1
                elif dy == 0.0:
                    T_y += 1
                elif (dx > 0 and dy > 0) or (dx < 0 and dy < 0):
                    C += 1
                else:
                    D += 1
        return C, D, T_x, T_y


@lru_cache(maxsize=128)
def _cached_ranks(ranks_tuple):
    return pd.Series(ranks_tuple).rank(method='min').values


# ===============================================================
# Zentrale Hilfsfunktionen für Gewichtung
# ===============================================================

def _weighted_mean(data, weight):
    data = np.asarray(data, dtype=np.float64)
    weight = np.asarray(weight, dtype=np.float64)
    return (data * weight).sum() / weight.sum()


def _weighted_var(data, weight):
    data = np.asarray(data, dtype=np.float64)
    weight = np.asarray(weight, dtype=np.float64)
    mean = _weighted_mean(data, weight)
    return ((data - mean) ** 2 * weight).sum() / weight.sum()


def _weighted_var_unbiased(data, weight):
    data = np.asarray(data, dtype=np.float64)
    weight = np.asarray(weight, dtype=np.float64)
    mean = _weighted_mean(data, weight)
    w_sum = weight.sum()
    w2_sum = (weight ** 2).sum()
    denom = w_sum - w2_sum / w_sum
    if denom <= 0:
        return np.nan
    return ((data - mean) ** 2 * weight).sum() / denom


def _weighted_std(data, weight):
    return np.sqrt(_weighted_var(data, weight))


def _weighted_count(weight):
    return np.asarray(weight, dtype=np.float64).sum()


def _effective_sample_size(weight):
    weight = np.asarray(weight, dtype=np.float64)
    w2_sum = (weight ** 2).sum()
    if w2_sum == 0:
        return 0.0
    return (weight.sum() ** 2) / w2_sum


def _calculate_average_deff(observed, expected, weight_series):
    weight_series = np.asarray(weight_series, dtype=np.float64)
    total_weight = weight_series.sum()
    sum_weight_squared = (weight_series ** 2).sum()
    if sum_weight_squared == 0:
        return 1.0
    return (total_weight ** 2) / sum_weight_squared


def _weighted_pearson(x, y, w):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    w = np.asarray(w, dtype=np.float64)
    w_sum = w.sum()
    mean_x = (x * w).sum() / w_sum
    mean_y = (y * w).sum() / w_sum
    dx = x - mean_x
    dy = y - mean_y
    cov_xy = (w * dx * dy).sum() / w_sum
    var_x = (w * dx ** 2).sum() / w_sum
    var_y = (w * dy ** 2).sum() / w_sum
    denom = np.sqrt(var_x * var_y)
    return cov_xy / denom if denom > 0 else np.nan


def _weighted_corr(df, weights):
    cols = df.columns
    data = df.values.astype(float)
    weights = np.asarray(weights, dtype=np.float64)
    w_sum = weights.sum()
    w_means = (data * weights[:, np.newaxis]).sum(axis=0) / w_sum
    centered = data - w_means
    weighted_centered = centered * np.sqrt(weights[:, np.newaxis])
    cov_matrix = (weighted_centered.T @ weighted_centered) / w_sum
    std_devs = np.sqrt(np.diag(cov_matrix))
    std_devs[std_devs == 0] = np.nan
    corr_matrix = cov_matrix / np.outer(std_devs, std_devs)
    np.fill_diagonal(corr_matrix, 1.0)
    return pd.DataFrame(corr_matrix, index=cols, columns=cols)


# ===============================================================
# Formatierungs-Hilfsfunktionen
# ===============================================================

def _format_p(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "n.b."
    if p >= 0.00001:
        return f"{p:.5f}"
    return f"{p:.2e}"


def _sig_stars(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "n.s."


def _validate_weight(weight, data_ref):
    if weight is None:
        return None
    if isinstance(weight, str):
        if isinstance(data_ref, pd.Series):
            raise ValueError(
                f"Gewichtung als String '{weight}' nicht möglich bei Series-Eingabe. "
                f"Bitte pd.Series als Gewichtung übergeben."
            )
        if not isinstance(data_ref, pd.DataFrame):
            raise ValueError(
                f"Gewichtung als String '{weight}' benötigt einen DataFrame."
            )
        if weight not in data_ref.columns:
            raise ValueError(
                f"Gewichtungsspalte '{weight}' nicht gefunden. "
                f"Vorhandene Spalten: {list(data_ref.columns)[:20]}"
            )
        weight = data_ref[weight]
    if not isinstance(weight, pd.Series):
        raise ValueError("weight muss ein Spaltenname (str) oder pd.Series sein.")
    if len(weight) != len(data_ref):
        raise ValueError(
            f"Gewichtungs-Serie (Länge {len(weight)}) muss dieselbe Länge "
            f"wie die Daten (Länge {len(data_ref)}) haben."
        )
    if weight.isna().any():
        n_missing = weight.isna().sum()
        warnings.warn(f"Gewichtung enthält {n_missing} NaN-Werte. Werden mit 0 ersetzt.")
        weight = weight.fillna(0)
    return weight


def _resolve_scale(scale):
    if not isinstance(scale, str):
        raise ValueError(
            f"scale muss ein String sein. Erhalten: {type(scale)}. "
            f"Erlaubt: 'nominal', 'ordinal', 'n', 'om'"
        )
    resolved = SCALE_ALIASES.get(scale.lower().strip(), None)
    if resolved is None:
        raise ValueError(
            f"Unbekannter Skalentyp: '{scale}'. "
            f"Erlaubt: 'nominal' (oder 'n', 'kategorial'), "
            f"'ordinal' (oder 'om', 'metrisch')"
        )
    return resolved


def _durbin_watson(residuals):
    diff = np.diff(residuals)
    return (diff ** 2).sum() / (residuals ** 2).sum()


# ===============================================================
# recode – Variablen umkodieren (ERWEITERT)
# ===============================================================

def _parse_recode_key(key_str, values):
    """
    Parst einen einzelnen Recode-Schlüssel und gibt eine boolesche Maske zurück.

    Unterstützte Formate:
        '1,2,4,6'     → exakte Werte (Komma-getrennt)
        '1-6'          → Bereich 1 bis 6 inklusive
        '>5'           → größer als 5
        '>=5'          → größer oder gleich 5
        '<3'           → kleiner als 3
        '<=3'          → kleiner oder gleich 3
        '>2 and <8'    → kombiniert mit AND
        '<2 or >8'     → kombiniert mit OR
        'not 5'        → alles außer 5
        'not 1,2,3'    → alles außer 1, 2, 3
        'else'         → alles was nicht zugeordnet wurde
    """
    values = pd.to_numeric(values, errors='coerce')

    key_str = str(key_str).strip()

    # 'else' → wird extern behandelt
    if key_str.lower() == 'else':
        return None

    # AND-Verknüpfung: '>2 and <8'
    if ' and ' in key_str.lower():
        parts = re.split(r'\s+and\s+', key_str, flags=re.IGNORECASE)
        mask = pd.Series(True, index=values.index)
        for part in parts:
            sub_mask = _parse_single_condition(part.strip(), values)
            mask = mask & sub_mask
        return mask

    # OR-Verknüpfung: '<2 or >8'
    if ' or ' in key_str.lower():
        parts = re.split(r'\s+or\s+', key_str, flags=re.IGNORECASE)
        mask = pd.Series(False, index=values.index)
        for part in parts:
            sub_mask = _parse_single_condition(part.strip(), values)
            mask = mask | sub_mask
        return mask

    return _parse_single_condition(key_str, values)


def _parse_single_condition(cond_str, values):
    """Parst eine einzelne Bedingung."""
    cond_str = cond_str.strip()

    # NOT: 'not 5' oder 'not 1,2,3'
    not_match = re.match(r'^not\s+(.+)$', cond_str, re.IGNORECASE)
    if not_match:
        inner = not_match.group(1).strip()
        inner_mask = _parse_single_condition(inner, values)
        return ~inner_mask

    # Bereich: '1-6' (mit Bindestrich, aber nicht negatives Vorzeichen)
    range_match = re.match(r'^(-?\d+\.?\d*)\s*-\s*(-?\d+\.?\d*)$', cond_str)
    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))
        return (values >= low) & (values <= high)

    # Vergleichsoperatoren: >=, <=, >, <
    comp_match = re.match(r'^(>=|<=|>|<)\s*(-?\d+\.?\d*)$', cond_str)
    if comp_match:
        op = comp_match.group(1)
        val = float(comp_match.group(2))
        if op == '>=':
            return values >= val
        elif op == '<=':
            return values <= val
        elif op == '>':
            return values > val
        elif op == '<':
            return values < val

    # Komma-getrennte Werte: '1,2,4,6'
    if ',' in cond_str:
        try:
            vals = [float(v.strip()) for v in cond_str.split(',')]
            return values.isin(vals)
        except ValueError:
            # Fallback: String-Vergleich
            vals = [v.strip() for v in cond_str.split(',')]
            return values.astype(str).isin(vals)

    # Einzelner numerischer Wert: '5'
    try:
        val = float(cond_str)
        return values == val
    except ValueError:
        pass

    # Einzelner String-Wert
    return values.astype(str) == cond_str


def recode(df, column, mapping, new_name=None, else_value=np.nan):
    """
    Rekodiert eine Variable nach einer Zuordnungstabelle.

    Parameter:
        df: pd.DataFrame
        column: str – Spaltenname der zu rekodierenden Variable
        mapping: dict – Zuordnung {Bedingung: neuer_Wert}

            Bedingungen (als String-Schlüssel):
                '1,2,4,6'       → exakte Werte 1, 2, 4 und 6
                '1-6'           → Bereich von 1 bis 6 (inklusive)
                '>5'            → größer als 5
                '>=5'           → größer oder gleich 5
                '<3'            → kleiner als 3
                '<=3'           → kleiner oder gleich 3
                '>2 and <8'     → kombiniert mit AND
                '<2 or >8'      → kombiniert mit OR
                'not 5'         → alles außer 5
                'not 1,2,3'     → alles außer 1, 2, 3
                'else'          → alles was nicht zugeordnet wurde

            Bedingungen (als Zahlen oder Tupel):
                5               → exakter Wert 5
                (1, 6)          → Bereich von 1 bis 6 (inklusive)

        new_name: str – Name der neuen Spalte (optional, sonst überschreiben)
        else_value: Wert für nicht zugeordnete Fälle (default: NaN)

    Rückgabe:
        pd.DataFrame mit neuer/überschriebener Spalte

    Beispiele:
        # Komma-getrennte Werte:
        df = recode(df, 'educ', {'1,2': 1, '3,4': 2, '5,6': 3},
                    new_name='educ3')

        # Bereiche mit Bindestrich:
        df = recode(df, 'alter', {'18-29': 1, '30-49': 2, '50-99': 3},
                    new_name='alter_kat')

        # Operatoren:
        df = recode(df, 'inc', {'<1000': 1, '>=1000 and <=3000': 2, '>3000': 3},
                    new_name='inc_kat')

        # NOT und ELSE:
        df = recode(df, 'item1', {'not 1,2': np.nan, 'else': 1},
                    new_name='item1_valid')

        # Likert-Skala invertieren:
        df = recode(df, 'item1', {1: 5, 2: 4, 3: 3, 4: 2, 5: 1},
                    new_name='item1_r')

        # Tupel-Bereiche:
        df = recode(df, 'alter', {(18, 29): 1, (30, 49): 2, (50, 99): 3},
                    new_name='alter_kat')
    """
    df = df.copy()
    target = new_name if new_name else column

    if column not in df.columns:
        raise ValueError(
            f"Spalte '{column}' nicht gefunden. "
            f"Vorhandene Spalten: {list(df.columns)[:20]}"
        )

    values = df[column].copy()
    result = pd.Series(np.nan, index=df.index, dtype=object)
    assigned = pd.Series(False, index=df.index)

    # Sortiere mapping: 'else' muss zuletzt kommen
    has_else = False
    else_val = else_value
    ordered_mapping = []

    for key, val in mapping.items():
        key_str = str(key).strip().lower() if isinstance(key, str) else str(key)
        if key_str == 'else':
            has_else = True
            else_val = val
        else:
            ordered_mapping.append((key, val))

    # Verarbeite alle Bedingungen
    for key, val in ordered_mapping:
        if isinstance(key, tuple) and len(key) == 2:
            # Tupel-Bereich: (low, high)
            low, high = key
            numeric_vals = pd.to_numeric(values, errors='coerce')
            mask = (numeric_vals >= low) & (numeric_vals <= high) & ~assigned
        elif isinstance(key, (int, float)):
            # Einzelner numerischer Wert
            numeric_vals = pd.to_numeric(values, errors='coerce')
            mask = (numeric_vals == key) & ~assigned
        elif isinstance(key, str):
            # String-Bedingung parsen
            mask = _parse_recode_key(key, values)
            if mask is None:
                continue
            mask = mask & ~assigned
        else:
            raise ValueError(f"Ungültiger Schlüsseltyp: {type(key)} für '{key}'")

        result[mask] = val
        assigned[mask] = True

    # else-Bedingung
    if has_else:
        result[~assigned] = else_val
    else:
        result[~assigned] = else_value

    df[target] = result

    # Versuche numerischen Typ
    try:
        df[target] = pd.to_numeric(df[target], errors='coerce')
        # Wenn alle Werte NaN oder numerisch sind, behalte numerisch
        if df[target].notna().any():
            pass
        else:
            df[target] = result  # Fallback auf Original
    except (ValueError, TypeError):
        pass

    # Info
    n_assigned = assigned.sum()
    n_unassigned = (~assigned).sum()
    n_nan = df[target].isna().sum()
    print(
        f"✅ recode: {column} → {target} "
        f"({n_assigned} zugeordnet, {n_unassigned} nicht zugeordnet, {n_nan} NaN)"
    )

    return df


# ===============================================================
# missing_report – Fehlende-Werte-Analyse
# ===============================================================

def missing_report(df, threshold=5.0):
    """
    Erstellt einen Bericht über fehlende Werte.

    Parameter:
        df: pd.DataFrame
        threshold: float – Warnschwelle in Prozent (default: 5%)

    Rückgabe:
        StatResult mit Tabelle sortiert nach Prozent fehlend

    Beispiel:
        result = missing_report(df)
        result.summary()
    """
    rows = []
    for col in df.columns:
        n_total = len(df)
        n_missing = df[col].isna().sum()
        n_valid = n_total - n_missing
        pct_missing = (n_missing / n_total) * 100

        if pct_missing > 0:
            flag = "🔴" if pct_missing > threshold * 2 else (
                "🟡" if pct_missing > threshold else "🟢"
            )
        else:
            flag = "✅"

        rows.append({
            "Variable": col,
            "n (gültig)": n_valid,
            "n (fehlend)": n_missing,
            "% fehlend": round(pct_missing, 2),
            "Status": flag
        })

    stat_df = pd.DataFrame(rows).sort_values("% fehlend", ascending=False).reset_index(drop=True)

    n_complete = (stat_df['n (fehlend)'] == 0).sum()
    n_problematic = (stat_df['% fehlend'] > threshold).sum()

    info = {
        "Variablen gesamt": len(df.columns),
        "Zeilen gesamt": len(df),
        "Vollständige Variablen": int(n_complete),
        "Mit Fehlenden": int(len(df.columns) - n_complete),
        f"Über {threshold}% fehlend": int(n_problematic),
        "Schwellenwert": f"{threshold}%"
    }

    return StatResult(
        tables={},
        stat=stat_df,
        test_name="Fehlende-Werte-Bericht",
        info=info
    )


# ===============================================================
# fre – Häufigkeitstabelle (NEUE SYNTAX: df, column)
# ===============================================================

def fre(df, column, weight=None, sort=True, round_digits=2):
    """
    Erstellt eine gewichtete Häufigkeitstabelle.

    Parameter:
        df: pd.DataFrame – Datensatz
        column: str – Spaltenname der zu analysierenden Variable
        weight: str (Spaltenname) oder pd.Series (optional)
        sort: nach Wert sortieren (default: True)
        round_digits: Dezimalstellen (default: 2)

    Rückgabe:
        pd.DataFrame

    Beispiel:
        fre(df, 'alter')
        fre(df, 'alter', weight='gewicht')
        fre(df, 'sex', sort=True)
    """
    # Validierung
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"Erster Parameter muss ein DataFrame sein, nicht {type(df).__name__}.\n"
            f"Syntax: fre(df, 'spaltenname')"
        )

    if not isinstance(column, str):
        raise TypeError(
            f"Zweiter Parameter muss ein Spaltenname (str) sein, nicht {type(column).__name__}.\n"
            f"Syntax: fre(df, 'spaltenname')"
        )

    if column not in df.columns:
        raise ValueError(
            f"Spalte '{column}' nicht gefunden. "
            f"Vorhandene Spalten: {list(df.columns)[:20]}"
        )

    data = df[column].copy()

    MisC = ["nan", "NaN", "N/A", "null", "None", ""]
    data_str = data.astype(str).replace(MisC, "Fehlend").fillna("Fehlend")

    # Gewichtung auflösen
    weight_series = _validate_weight(weight, df)

    if weight_series is not None:
        weighted_freq = data_str.groupby(data_str).apply(
            lambda x: weight_series.loc[x.index].sum()
        )
        HT = pd.DataFrame({
            "Ausprägung": weighted_freq.index,
            "Häufigkeiten": weighted_freq.values
        })
    else:
        freq = data_str.value_counts(dropna=False)
        HT = pd.DataFrame({
            "Ausprägung": freq.index,
            "Häufigkeiten": freq.values
        })

    HT["Häufigkeiten"] = HT["Häufigkeiten"].round(0).astype("int32")

    HT["__sort_value__"] = pd.to_numeric(HT["Ausprägung"], errors='coerce')
    HT = HT.sort_values("__sort_value__", ascending=True).drop("__sort_value__", axis=1)

    total = HT["Häufigkeiten"].sum()
    HT["Prozent"] = (HT["Häufigkeiten"] / total) * 100
    HT["kum. Prozente"] = HT["Häufigkeiten"].cumsum() / total * 100

    valid_sum = total - HT[HT["Ausprägung"] == "Fehlend"]["Häufigkeiten"].sum()
    valid_sum = max(valid_sum, 1)
    validP = (HT["Häufigkeiten"] / valid_sum) * 100
    is_missing = HT["Ausprägung"].isin(MisC + ["Fehlend"])
    validP[is_missing] = np.nan
    HT["gültigeP"] = validP
    HT["kum.gültigeP"] = HT["gültigeP"].cumsum()

    HT = HT[["Ausprägung", "Häufigkeiten", "Prozent", "kum. Prozente", "gültigeP", "kum.gültigeP"]]

    for c in ["Prozent", "kum. Prozente", "gültigeP", "kum.gültigeP"]:
        HT[c] = HT[c].round(round_digits)

    n_total = HT["Häufigkeiten"].sum()
    missing_count = HT[HT["Ausprägung"] == "Fehlend"]["Häufigkeiten"].sum()
    n_valid = n_total - missing_count

    n_row = pd.DataFrame({
        "Ausprägung": ["Summe"], "Häufigkeiten": [n_total],
        "Prozent": [np.nan], "kum. Prozente": [np.nan],
        "gültigeP": [np.nan], "kum.gültigeP": [np.nan]
    })
    n_nan_row = pd.DataFrame({
        "Ausprägung": ["n-nan="], "Häufigkeiten": [n_valid],
        "Prozent": [np.nan], "kum. Prozente": [np.nan],
        "gültigeP": [np.nan], "kum.gültigeP": [np.nan]
    })

    HT = pd.concat([HT, n_row, n_nan_row], ignore_index=True)

    for c in ["Prozent", "kum. Prozente", "gültigeP", "kum.gültigeP"]:
        HT[c] = HT[c].replace([np.nan], "---")

    return HT


# ===============================================================
# fre_wl – Häufigkeitstabelle mit Labels (NEUE SYNTAX: df, column, labels_df/series)
# ===============================================================

def fre_wl(df, column, labels, weight=None, sort_by_value=True, round_digits=2):
    """
    Kombinierte Häufigkeitstabelle mit Labels.

    Parameter:
        df: pd.DataFrame – Datensatz mit numerischen Ausprägungen
        column: str – Spaltenname der zu analysierenden Variable
        labels: pd.DataFrame oder pd.Series – Labels
            - pd.DataFrame: muss dieselbe Spalte enthalten (z.B. dfL['spalte'])
            - pd.Series: wird direkt als Label-Spalte verwendet
        weight: str (Spaltenname) oder pd.Series (optional)
        sort_by_value: nach Wert sortieren (default: True)
        round_digits: Dezimalstellen (default: 2)

    Rückgabe:
        pd.DataFrame

    Beispiel:
        fre_wl(df, 'v173', dfL)
        fre_wl(df, 'v173', dfL, weight='gewicht')
        fre_wl(df, 'v173', dfL['v173'])
    """
    # Validierung
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"Erster Parameter muss ein DataFrame sein, nicht {type(df).__name__}.\n"
            f"Syntax: fre_wl(df, 'spaltenname', labels_df)"
        )

    if not isinstance(column, str):
        raise TypeError(
            f"Zweiter Parameter muss ein Spaltenname (str) sein, nicht {type(column).__name__}.\n"
            f"Syntax: fre_wl(df, 'spaltenname', labels_df)"
        )

    if column not in df.columns:
        raise ValueError(
            f"Spalte '{column}' nicht gefunden in df. "
            f"Vorhandene Spalten: {list(df.columns)[:20]}"
        )

    # Labels auflösen
    if isinstance(labels, pd.DataFrame):
        if column not in labels.columns:
            raise ValueError(
                f"Spalte '{column}' nicht gefunden im Labels-DataFrame. "
                f"Vorhandene Spalten: {list(labels.columns)[:20]}"
            )
        label_series = labels[column].copy()
    elif isinstance(labels, pd.Series):
        label_series = labels.copy()
    elif isinstance(labels, (list, np.ndarray)):
        label_series = pd.Series(labels)
    else:
        raise TypeError(
            f"labels muss ein DataFrame, Series, Liste oder Array sein, "
            f"nicht {type(labels).__name__}.\n"
            f"Syntax: fre_wl(df, 'spaltenname', labels_df)"
        )

    data = df[column].copy()

    if len(data) != len(label_series):
        raise ValueError(
            f"Länge von data ({len(data)}) und labels ({len(label_series)}) ungleich."
        )

    df_temp = pd.DataFrame({"Ausprägung": data, "Label": label_series})
    MisC = ["nan", "NaN", "N/A", "null", "None", ""]
    df_temp["Label"] = df_temp["Label"].astype(str).replace(MisC, "---").fillna("---")

    # Gewichtung auflösen
    weight_series = _validate_weight(weight, df)

    if weight_series is not None:
        weighted_freq = df_temp.groupby("Ausprägung").apply(
            lambda x: weight_series.loc[x.index].sum()
        )
        HT = pd.DataFrame({"Ausprägung": weighted_freq.index, "Häufigkeiten": weighted_freq.values})
    else:
        freq = df_temp["Ausprägung"].value_counts(dropna=False)
        HT = pd.DataFrame({"Ausprägung": freq.index, "Häufigkeiten": freq.values})

    HT["Häufigkeiten"] = HT["Häufigkeiten"].round(0).astype("int32")
    label_map = df_temp.drop_duplicates(subset="Ausprägung").set_index("Ausprägung")["Label"].to_dict()
    HT["Label"] = HT["Ausprägung"].map(label_map).fillna("---")

    total = HT["Häufigkeiten"].sum()
    HT["Prozent"] = (HT["Häufigkeiten"] / total) * 100
    HT["kum. Prozente"] = HT["Häufigkeiten"].cumsum() / total * 100

    valid_rows = HT[HT["Ausprägung"] != "Fehlend"]
    valid_sum = max(valid_rows["Häufigkeiten"].sum(), 1)
    HT["gültigeP"] = np.nan
    HT.loc[valid_rows.index, "gültigeP"] = (
        (valid_rows["Häufigkeiten"] / valid_sum) * 100
    ).round(round_digits)
    HT["kum.gültigeP"] = np.nan
    HT.loc[valid_rows.index, "kum.gültigeP"] = (
        (valid_rows["Häufigkeiten"].cumsum() / valid_sum) * 100
    ).round(round_digits)

    HT = HT[["Ausprägung", "Label", "Häufigkeiten", "Prozent",
             "kum. Prozente", "gültigeP", "kum.gültigeP"]]
    HT["Prozent"] = HT["Prozent"].round(round_digits)
    HT["kum. Prozente"] = HT["kum. Prozente"].round(round_digits)

    if sort_by_value:
        HT["__sort"] = pd.to_numeric(HT["Ausprägung"], errors='coerce')
        HT = HT.sort_values("__sort", ascending=True).drop("__sort", axis=1)

    n_total = HT["Häufigkeiten"].sum()
    missing_count = HT[HT["Label"] == "---"]["Häufigkeiten"].sum()

    n_row = pd.DataFrame({
        "Ausprägung": ["Summe"], "Label": ["---"], "Häufigkeiten": [n_total],
        "Prozent": [np.nan], "kum. Prozente": [np.nan],
        "gültigeP": [np.nan], "kum.gültigeP": [np.nan]
    })
    n_nan_row = pd.DataFrame({
        "Ausprägung": ["n-nan="], "Label": ["---"],
        "Häufigkeiten": [n_total - missing_count],
        "Prozent": [np.nan], "kum. Prozente": [np.nan],
        "gültigeP": [np.nan], "kum.gültigeP": [np.nan]
    })

    HT = pd.concat([HT, n_row, n_nan_row], ignore_index=True)
    for c in ["Prozent", "kum. Prozente", "gültigeP", "kum.gültigeP"]:
        HT[c] = HT[c].replace([np.nan], "---")

    return HT


# ===============================================================
# uniV – Univariate Analyse
# ===============================================================

def uniV(df, column_name, weight=None, se=False):
    """
    Univariate Analyse mit optionaler Gewichtung.

    Parameter:
        df: pd.DataFrame
        column_name: str
        weight: str oder pd.Series (optional)
        se: bool – Standardfehler (default: False)

    Rückgabe:
        StatResult mit result['fre'] und result['stats']

    Beispiel:
        result = uniV(df, 'alter')
        result.summary()
    """
    df = df.copy()
    if column_name not in df.columns:
        raise ValueError(
            f"Spalte '{column_name}' nicht gefunden. "
            f"Vorhandene: {list(df.columns)[:20]}"
        )

    weight_series = _validate_weight(weight, df)

    # fre intern mit der neuen Syntax aufrufen
    fre_table = _fre_internal(df[column_name], weight=weight_series,
                               sort=False, round_digits=2)

    stats_table = None
    numeric_data = pd.to_numeric(df[column_name], errors='coerce')
    valid_data = numeric_data.dropna()
    info = {"Variable": column_name, "n (gesamt)": len(df),
            "n (gültig)": len(valid_data)}

    if len(valid_data) > 0:
        q25 = valid_data.quantile(0.25)
        q50 = valid_data.quantile(0.50)
        q75 = valid_data.quantile(0.75)
        modes = valid_data.mode()
        mode_str = (str(modes[0]) if len(modes) == 1
                    else ", ".join(map(str, modes)))

        if weight_series is not None:
            wv = weight_series.loc[valid_data.index]
            mean_val = _weighted_mean(valid_data, wv)
            variance = _weighted_var(valid_data, wv)
            std_val = _weighted_std(valid_data, wv)
            n_eff = _effective_sample_size(wv)
            info["n (effektiv)"] = round(n_eff, 2)
        else:
            mean_val = valid_data.mean()
            variance = valid_data.var(ddof=1)
            std_val = valid_data.std(ddof=1)
            n_eff = len(valid_data)

        t_crit = stats.t.ppf(0.975, df=max(n_eff - 1, 1))
        me = t_crit * (std_val / np.sqrt(max(n_eff, 1)))

        stats_dict = {
            "Modus": mode_str,
            "25%-Quantil": q25,
            "50%-Quantil (Median)": q50,
            "75%-Quantil": q75,
            "IQR": q75 - q25,
            "Mittelwert": mean_val,
            "95%-KI (untere Grenze)": mean_val - me,
            "95%-KI (obere Grenze)": mean_val + me,
            "Minimum": valid_data.min(),
            "Maximum": valid_data.max(),
            "Varianz": variance,
            "Standardabweichung": std_val,
            "Schiefe": valid_data.skew(),
            "Kurtosis": valid_data.kurtosis(),
            "Exzess": valid_data.kurtosis() - 3
        }

        se_map = {
            "Mittelwert": std_val / np.sqrt(n_eff) if n_eff > 1 else np.nan,
            "Varianz": variance / np.sqrt(2 * n_eff) if n_eff > 1 else np.nan,
            "Standardabweichung": (std_val / np.sqrt(2 * n_eff)
                                   if n_eff > 1 else np.nan),
            "Schiefe": np.sqrt(6 / n_eff) if n_eff > 1 else np.nan,
            "Kurtosis": np.sqrt(24 / n_eff) if n_eff > 1 else np.nan
        }

        stats_list = []
        for stat, val in stats_dict.items():
            row = {
                "Statistik": stat,
                "Wert": (f"{val:.4f}" if stat in se_map
                         else (f"{val:.2f}" if isinstance(val, (int, float))
                               else val))
            }
            if se:
                row["SE"] = (f"{se_map[stat]:.4f}" if stat in se_map
                             else "---")
            stats_list.append(row)
        stats_table = pd.DataFrame(stats_list)
    else:
        names = ["Modus", "25%-Quantil", "Median", "75%-Quantil", "IQR",
                 "Mittelwert", "95%-KI unten", "95%-KI oben", "Min", "Max",
                 "Varianz", "SD", "Schiefe", "Kurtosis", "Exzess"]
        stats_table = pd.DataFrame(
            {"Statistik": names, "Wert": [np.nan] * 15}
        )
        if se:
            stats_table["SE"] = "---"

    return StatResult(
        tables={"fre": fre_table},
        stat=stats_table,
        test_name=f"Univariate Analyse: {column_name}",
        info=info
    )


def _fre_internal(data_series, weight=None, sort=True, round_digits=2):
    """
    Interne Häufigkeitstabelle für pd.Series (wird von uniV genutzt).
    """
    data = data_series.copy()
    MisC = ["nan", "NaN", "N/A", "null", "None", ""]
    data_str = data.astype(str).replace(MisC, "Fehlend").fillna("Fehlend")

    weight_series = None
    if weight is not None:
        if isinstance(weight, pd.Series):
            if len(weight) != len(data_str):
                raise ValueError(
                    "Gewichtung muss dieselbe Länge wie die Daten haben."
                )
            weight_series = weight
        else:
            raise ValueError("weight muss eine pd.Series sein.")

    if weight_series is not None:
        weighted_freq = data_str.groupby(data_str).apply(
            lambda x: weight_series.loc[x.index].sum()
        )
        HT = pd.DataFrame({
            "Ausprägung": weighted_freq.index,
            "Häufigkeiten": weighted_freq.values
        })
    else:
        freq = data_str.value_counts(dropna=False)
        HT = pd.DataFrame({
            "Ausprägung": freq.index,
            "Häufigkeiten": freq.values
        })

    HT["Häufigkeiten"] = HT["Häufigkeiten"].round(0).astype("int32")

    HT["__sort_value__"] = pd.to_numeric(HT["Ausprägung"], errors='coerce')
    HT = HT.sort_values("__sort_value__", ascending=True).drop(
        "__sort_value__", axis=1
    )

    total = HT["Häufigkeiten"].sum()
    HT["Prozent"] = (HT["Häufigkeiten"] / total) * 100
    HT["kum. Prozente"] = HT["Häufigkeiten"].cumsum() / total * 100

    valid_sum = (total
                 - HT[HT["Ausprägung"] == "Fehlend"]["Häufigkeiten"].sum())
    valid_sum = max(valid_sum, 1)
    validP = (HT["Häufigkeiten"] / valid_sum) * 100
    is_missing = HT["Ausprägung"].isin(MisC + ["Fehlend"])
    validP[is_missing] = np.nan
    HT["gültigeP"] = validP
    HT["kum.gültigeP"] = HT["gültigeP"].cumsum()

    HT = HT[["Ausprägung", "Häufigkeiten", "Prozent",
             "kum. Prozente", "gültigeP", "kum.gültigeP"]]

    for c in ["Prozent", "kum. Prozente", "gültigeP", "kum.gültigeP"]:
        HT[c] = HT[c].round(round_digits)

    n_total = HT["Häufigkeiten"].sum()
    missing_count = HT[HT["Ausprägung"] == "Fehlend"]["Häufigkeiten"].sum()
    n_valid = n_total - missing_count

    n_row = pd.DataFrame({
        "Ausprägung": ["Summe"], "Häufigkeiten": [n_total],
        "Prozent": [np.nan], "kum. Prozente": [np.nan],
        "gültigeP": [np.nan], "kum.gültigeP": [np.nan]
    })
    n_nan_row = pd.DataFrame({
        "Ausprägung": ["n-nan="], "Häufigkeiten": [n_valid],
        "Prozent": [np.nan], "kum. Prozente": [np.nan],
        "gültigeP": [np.nan], "kum.gültigeP": [np.nan]
    })

    HT = pd.concat([HT, n_row, n_nan_row], ignore_index=True)

    for c in ["Prozent", "kum. Prozente", "gültigeP", "kum.gültigeP"]:
        HT[c] = HT[c].replace([np.nan], "---")

    return HT


# ===============================================================
# cross_tab – Kreuztabelle
# ===============================================================

def cross_tab(df, col1, col2, weight=None, round_digits=2,
              show_expected=True, show_residuals=True,
              show_deff=True, show_deff_p=True):
    """
    Gewichtete Kreuztabelle.

    Rückgabe:
        StatResult mit observed, col_percent, row_percent, etc.

    Beispiel:
        ct = cross_tab(df, 'sex', 'educ')
        ct.summary(show_tables=True)
    """
    if col1 not in df.columns:
        raise ValueError(f"Spalte '{col1}' nicht gefunden.")
    if col2 not in df.columns:
        raise ValueError(f"Spalte '{col2}' nicht gefunden.")

    df = df.copy()
    MisC = ["nan", "NaN", "N/A", "null", "None", ""]
    df[col1] = df[col1].astype(str).replace(MisC, np.nan)
    df[col2] = df[col2].astype(str).replace(MisC, np.nan)
    df_clean = df.dropna(subset=[col1, col2])

    if df_clean.empty:
        raise ValueError("Keine Daten nach Entfernung fehlender Werte.")

    weight_series = _validate_weight(weight, df_clean)

    if weight_series is not None:
        observed = pd.crosstab(
            df_clean[col1], df_clean[col2], margins=True,
            margins_name="Gesamt",
            values=weight_series, aggfunc='sum'
        ).fillna(0)
    else:
        observed = pd.crosstab(
            df_clean[col1], df_clean[col2],
            margins=True, margins_name="Gesamt"
        )

    observed.columns.name = col2
    observed.index.name = col1
    total = observed.loc["Gesamt", "Gesamt"]
    if total == 0:
        raise ValueError("Gesamtsumme ist 0.")

    expected = pd.DataFrame(
        index=observed.index, columns=observed.columns, dtype=float
    )
    st_residuals = pd.DataFrame(
        index=observed.index, columns=observed.columns, dtype=float
    )
    residuals = pd.DataFrame(
        index=observed.index, columns=observed.columns, dtype=float
    )

    for row in observed.index:
        for col in observed.columns:
            if row == "Gesamt" or col == "Gesamt":
                expected.loc[row, col] = np.nan
                st_residuals.loc[row, col] = np.nan
                residuals.loc[row, col] = np.nan
            else:
                exp = (observed.loc[row, "Gesamt"]
                       * observed.loc["Gesamt", col] / total)
                expected.loc[row, col] = exp
                res = observed.loc[row, col] - exp
                residuals.loc[row, col] = res
                st_residuals.loc[row, col] = (
                    res / np.sqrt(exp) if exp > 0 else np.nan
                )

    deff = pd.DataFrame(
        index=observed.index, columns=observed.columns, dtype=float
    )
    p_value_deff = pd.DataFrame(
        index=observed.index, columns=observed.columns, dtype=float
    )
    info = {"Zeilen": col1, "Spalten": col2, "n": int(total)}

    if weight_series is not None:
        for row in observed.index:
            for col in observed.columns:
                if row == "Gesamt" or col == "Gesamt":
                    deff.loc[row, col] = np.nan
                else:
                    w_ij = weight_series.loc[
                        (df_clean[col1] == row) & (df_clean[col2] == col)
                    ]
                    deff.loc[row, col] = (
                        (w_ij.sum() ** 2) / (w_ij ** 2).sum()
                        if len(w_ij) > 0 else np.nan
                    )

        deff_avg = _calculate_average_deff(
            observed, expected, weight_series
        )
        obs_nm = observed.drop("Gesamt", axis=0).drop("Gesamt", axis=1)
        chi2_s, p_raw, dof_val, _ = chi2_contingency(obs_nm)
        chi2_corr = chi2_s / deff_avg
        p_corr = 1 - chi2.cdf(chi2_corr, dof_val)
        info.update({
            "Chi²": round(chi2_s, 4),
            "DEFF": round(deff_avg, 4),
            "Chi² (korr.)": round(chi2_corr, 4),
            "p (korr.)": round(p_corr, 5)
        })

        for row in observed.index:
            for col in observed.columns:
                p_value_deff.loc[row, col] = (
                    np.nan if row == "Gesamt" or col == "Gesamt"
                    else p_corr
                )

    observed = observed.round(0).astype("int32")
    for t in [expected, st_residuals, residuals, deff, p_value_deff]:
        t.iloc[:] = t.round(round_digits) if hasattr(t, 'round') else t

    col_pct = (
        observed.div(observed.loc["Gesamt"], axis=1) * 100
    ).round(round_digits)
    row_pct = (
        observed.div(observed["Gesamt"], axis=0) * 100
    ).round(round_digits)
    total_pct = (observed / total * 100).round(round_digits)

    tables = {
        "observed": observed,
        "col_percent": col_pct,
        "row_percent": row_pct,
        "total_percent": total_pct,
        "residuals": residuals
    }
    if show_expected:
        tables["expected"] = expected
    if show_residuals:
        tables["st_residuals"] = st_residuals
    if show_deff:
        tables["deff"] = deff
    if show_deff_p:
        tables["p_value_deff"] = p_value_deff

    return StatResult(
        tables=tables, stat=None,
        test_name=f"Kreuztabelle: {col1} × {col2}",
        info=info
    )


# ===============================================================
# biV – Bivariate Analyse
# ===============================================================

def _calc_om_stats(x, y, w, rd):
    results = []
    if w is not None:
        r = _weighted_pearson(x, y, w)
        n_eff = _effective_sample_size(w)
        p_r = (
            2 * (1 - stats.t.cdf(
                abs(r * np.sqrt((n_eff - 2) / (1 - r ** 2))), n_eff - 2
            )) if abs(r) < 1 and n_eff > 2 else np.nan
        )
    else:
        r, p_r = pearsonr(x, y)
    results.append({
        "Maß": "Pearson-r",
        "Wert": f"{r:.{rd + 2}f}",
        "p-Wert": _format_p(p_r),
        "Sig.": _sig_stars(p_r)
    })

    rho, p_rho = spearmanr(x, y)
    results.append({
        "Maß": "Spearman-Rho",
        "Wert": f"{rho:.{rd + 2}f}",
        "p-Wert": _format_p(p_rho),
        "Sig.": _sig_stars(p_rho)
    })

    tau, p_tau = kendalltau(x, y)
    results.append({
        "Maß": "Kendall's Tau-b",
        "Wert": f"{tau:.{rd + 2}f}",
        "p-Wert": _format_p(p_tau),
        "Sig.": _sig_stars(p_tau)
    })

    C, D, T_x, T_y = _count_concordant_discordant_full(x, y)
    n = len(x)
    tp = n * (n - 1) / 2

    denom_yx = C + D + T_x
    d_yx = (C - D) / denom_yx if denom_yx > 0 else np.nan
    p_yx = _somers_d_pvalue(C, D, denom_yx, tp)

    denom_xy = C + D + T_y
    d_xy = (C - D) / denom_xy if denom_xy > 0 else np.nan
    p_xy = _somers_d_pvalue(C, D, denom_xy, tp)

    results.append({
        "Maß": "Somers' D (Y|X)",
        "Wert": (f"{d_yx:.{rd + 2}f}" if not np.isnan(d_yx) else "n.b."),
        "p-Wert": _format_p(p_yx),
        "Sig.": _sig_stars(p_yx)
    })
    results.append({
        "Maß": "Somers' D (X|Y)",
        "Wert": (f"{d_xy:.{rd + 2}f}" if not np.isnan(d_xy) else "n.b."),
        "p-Wert": _format_p(p_xy),
        "Sig.": _sig_stars(p_xy)
    })
    return results


def _somers_d_pvalue(C, D, denom, total_pairs):
    if denom <= 0 or total_pairs <= 0:
        return np.nan
    d_stat = (C - D) / denom
    ase0 = (np.sqrt(4 * (C + D) / (denom ** 2))
            if (C + D) > 0 else np.nan)
    if ase0 is None or np.isnan(ase0) or ase0 <= 0:
        return np.nan
    return 2 * (1 - stats.norm.cdf(abs(d_stat / ase0)))


def _calc_n_stats(data, col1, col2, w, rd):
    results = []
    if w is not None:
        ct = pd.crosstab(
            data[col1], data[col2],
            values=pd.Series(w, index=data.index), aggfunc='sum'
        ).fillna(0)
    else:
        ct = pd.crosstab(data[col1], data[col2])

    if ct.empty:
        return [{
            "Maß": "Keine Daten", "Wert": "n.b.",
            "p-Wert": "n.b.", "Sig.": ""
        }]

    n_total = ct.sum().sum()
    r, c = ct.shape
    chi2_s, pv, dof, _ = chi2_contingency(ct)
    label = "Chi²"

    if w is not None:
        wa = np.asarray(w, dtype=np.float64)
        deff_g = (wa.sum() ** 2) / (len(wa) * (wa ** 2).sum())
        if deff_g > 0:
            pv = 1 - chi2.cdf(chi2_s / deff_g, dof)
        label = "Chi² (DEFF-korr.)"

    results.append({
        "Maß": label,
        "Wert": f"{chi2_s:.{rd + 2}f}",
        "p-Wert": _format_p(pv),
        "Sig.": _sig_stars(pv)
    })

    exp_m = np.outer(ct.sum(axis=1), ct.sum(axis=0)) / n_total
    lr = sum(
        2 * ct.iloc[i, j] * np.log(ct.iloc[i, j] / exp_m[i, j])
        for i in range(r) for j in range(c)
        if ct.iloc[i, j] > 0 and exp_m[i, j] > 0
    )
    dof_lr = (r - 1) * (c - 1)
    p_lr = 1 - chi2.cdf(lr, dof_lr)
    results.append({
        "Maß": "G²",
        "Wert": f"{lr:.{rd + 2}f}",
        "p-Wert": _format_p(p_lr),
        "Sig.": _sig_stars(p_lr)
    })

    k = min(r, c) - 1
    if r == 2 and c == 2:
        phi = np.sqrt(chi2_s / n_total) if n_total > 0 else np.nan
        results.append({
            "Maß": "Phi (φ)",
            "Wert": (f"{phi:.{rd + 2}f}" if not np.isnan(phi) else "n.b."),
            "p-Wert": "---",
            "Sig.": ""
        })
    else:
        cv = (np.sqrt(chi2_s / (n_total * k))
              if k > 0 and n_total > 0 else np.nan)
        results.append({
            "Maß": "Cramér's V",
            "Wert": (f"{cv:.{rd + 2}f}" if not np.isnan(cv) else "n.b."),
            "p-Wert": "---",
            "Sig.": ""
        })

    return results


def biV(df, col1, col2, scale, weight=None, round_digits=2, notable=False):
    """
    Bivariate Analyse.

    Parameter:
        df: pd.DataFrame
        col1, col2: str
        scale: 'nominal'/'n' oder 'ordinal'/'om'
        weight: str oder pd.Series (optional)
        round_digits: int (default: 2)
        notable: bool – nur Statistiken (default: False)

    Rückgabe:
        StatResult

    Beispiel:
        biV(df, 'sex', 'educ', 'nominal').summary()
        biV(df, 'age', 'inc', 'ordinal').summary()
    """
    scale = _resolve_scale(scale)

    for c in [col1, col2]:
        if c not in df.columns:
            raise ValueError(
                f"Spalte '{c}' nicht gefunden. "
                f"Vorhanden: {list(df.columns)[:20]}"
            )

    cols_needed = [col1, col2]
    weight_col = None
    if isinstance(weight, str) and weight is not None:
        if weight not in df.columns:
            raise ValueError(
                f"Gewichtungsspalte '{weight}' nicht gefunden."
            )
        cols_needed.append(weight)
        weight_col = weight

    data = df[cols_needed].dropna().copy()
    if len(data) < 2:
        return StatResult(
            stat=pd.DataFrame({
                "Maß": ["Keine Paare"],
                "Wert": [np.nan],
                "p-Wert": [np.nan],
                "Sig.": [""]
            }),
            test_name=f"biV: {col1} × {col2}"
        )

    data[col1] = pd.to_numeric(data[col1], errors='coerce')
    data[col2] = pd.to_numeric(data[col2], errors='coerce')
    data = data.dropna(subset=[col1, col2])

    w = (data[weight_col].values.astype(float) if weight_col
         else (weight.loc[data.index].values.astype(float)
               if isinstance(weight, pd.Series) else None))

    tables = {}
    if not notable:
        try:
            tables["cross_tab"] = cross_tab(
                df, col1, col2, weight=weight,
                round_digits=round_digits
            )
        except Exception as e:
            warnings.warn(f"Kreuztabelle fehlgeschlagen: {e}")

    x = data[col1].values.astype(float)
    y = data[col2].values.astype(float)
    sl = "nominal" if scale == "n" else "ordinal-metrisch"

    if scale == "om":
        results = _calc_om_stats(x, y, w, round_digits)
    else:
        results = _calc_n_stats(data, col1, col2, w, round_digits)

    stat_df = pd.DataFrame(results)
    stat_df["Wert"] = stat_df["Wert"].astype(str)
    stat_df["p-Wert"] = stat_df["p-Wert"].astype(str)

    return StatResult(
        tables=tables, stat=stat_df,
        test_name=f"Bivariate Analyse: {col1} × {col2} ({sl})",
        info={
            "Variablen": f"{col1} × {col2}",
            "Skalenniveau": sl,
            "n": len(data),
            "Gewichtung": (weight_col
                           or ("pd.Series" if w is not None else "keine"))
        }
    )


# ===============================================================
# ttest_u – Unabhängiger t-Test
# ===============================================================

def ttest_u(group, g1, g2, dependent, data=None, weight=None,
            levene_test='median', autoLevene=True):
    """
    Unabhängiger t-Test mit optionaler Gewichtung.

    Parameter:
        group: str – Gruppenvariable
        g1, g2: Ausprägungen
        dependent: str – Abhängige Variable
        data: pd.DataFrame
        weight: str oder pd.Series (optional)
        levene_test: 'mean', 'median', 'trimmed'
        autoLevene: bool (default: True)

    Rückgabe:
        StatResult

    Beispiel:
        ttest_u(group='sex', g1=1, g2=2,
                dependent='inc', data=df).summary()
    """
    if data is None:
        raise ValueError("data muss übergeben werden.")
    for v in [group, dependent]:
        if v not in data.columns:
            raise ValueError(
                f"Variable '{v}' fehlt. "
                f"Vorhanden: {list(data.columns)[:20]}"
            )

    gs = data[group].dropna()
    uv = gs.unique()
    is_num = np.issubdtype(gs.dtype, np.number)
    if is_num:
        try:
            g1, g2 = float(g1), float(g2)
        except:
            raise ValueError(
                f"Gruppenwerte müssen numerisch sein: g1={g1}, g2={g2}"
            )
    else:
        g1, g2 = str(g1), str(g2)

    for g in [g1, g2]:
        if g not in uv:
            raise ValueError(
                f"Gruppe '{g}' nicht in '{group}'. "
                f"Vorhanden: {sorted(uv)}"
            )

    cols = [group, dependent]
    wc = None
    if isinstance(weight, str) and weight is not None:
        if weight not in data.columns:
            raise ValueError(
                f"Gewichtungsspalte '{weight}' nicht gefunden."
            )
        cols.append(weight)
        wc = weight

    dg = data[cols].dropna().copy()
    m1, m2 = dg[dg[group] == g1], dg[dg[group] == g2]
    g1d = m1[dependent].values.astype(float)
    g2d = m2[dependent].values.astype(float)

    hw = False
    w1 = w2 = None
    if wc:
        w1 = m1[wc].values.astype(float)
        w2 = m2[wc].values.astype(float)
        hw = True
    elif isinstance(weight, pd.Series):
        w1 = weight.loc[m1.index].values.astype(float)
        w2 = weight.loc[m2.index].values.astype(float)
        hw = True

    for gn, gd in [(g1, g1d), (g2, g2d)]:
        if len(gd) < 2:
            raise ValueError(
                f"Gruppe '{gn}' hat nur {len(gd)} Wert(e). Min. 2 nötig."
            )

    lp = np.nan
    lpf = "---"
    ul = False
    dec = "Welch-t-Test"

    if hw:
        warnings.warn(
            "Levene bei Gewichtung nicht durchgeführt. "
            "Welch-t wird verwendet."
        )
    else:
        ul = True
        if levene_test in ('mean', 'median', 'trimmed'):
            lv = levene(g1d, g2d, center=levene_test)
        else:
            raise ValueError(
                f"levene_test muss 'mean', 'median' oder 'trimmed' sein."
            )
        lp = lv.pvalue
        lpf = f"{lp:.5f}" if lp >= 0.00001 else f"{lp:.2e}"
        dec = ("Student-t-Test" if lp > 0.05 else "Welch-t-Test")

    n1r, n2r = len(g1d), len(g2d)
    if hw:
        mn1 = _weighted_mean(g1d, w1)
        mn2 = _weighted_mean(g2d, w2)
        v1 = _weighted_var_unbiased(g1d, w1)
        v2 = _weighted_var_unbiased(g2d, w2)
        ne1 = _effective_sample_size(w1)
        ne2 = _effective_sample_size(w2)
    else:
        mn1, mn2 = np.mean(g1d), np.mean(g2d)
        v1 = np.var(g1d, ddof=1)
        v2 = np.var(g2d, ddof=1)
        ne1, ne2 = float(n1r), float(n2r)

    md = mn1 - mn2

    # Student-t
    dfe = ne1 + ne2 - 2
    if hw:
        sp2 = (((ne1 - 1) * v1 + (ne2 - 1) * v2) / dfe
               if dfe > 0 else np.nan)
        see = (np.sqrt(sp2 * (1 / ne1 + 1 / ne2))
               if sp2 and sp2 > 0 else np.nan)
        tse = md / see if see and see > 0 else np.nan
        pve = (2 * (1 - stats.t.cdf(abs(tse), dfe))
               if not np.isnan(tse) and dfe > 0 else np.nan)
    else:
        tse, pve = ttest_ind(g1d, g2d, equal_var=True)

    # Welch-t
    v1n = v1 / ne1 if ne1 > 0 else np.nan
    v2n = v2 / ne2 if ne2 > 0 else np.nan
    seu = (np.sqrt(v1n + v2n)
           if v1n is not None and v2n is not None else np.nan)

    if hw:
        tsu = md / seu if seu and seu > 0 else np.nan
    else:
        tsu, _ = ttest_ind(g1d, g2d, equal_var=False)

    if v1n and v2n and ne1 > 1 and ne2 > 1:
        num = (v1n + v2n) ** 2
        den = (v1n ** 2) / (ne1 - 1) + (v2n ** 2) / (ne2 - 1)
        dfu = num / den if den > 0 else np.nan
    else:
        dfu = np.nan

    pvu = (2 * (1 - stats.t.cdf(abs(tsu), dfu))
           if not np.isnan(tsu) and not np.isnan(dfu) and dfu > 0
           else np.nan)

    if autoLevene and ul:
        if lp > 0.05:
            tn = "Student-t-Test (Varianzhomogenität)"
            ts, pv, dfv = tse, pve, dfe
            se_used = see if hw else np.sqrt(v1 / ne1 + v2 / ne2)
        else:
            tn = "Welch-t-Test (keine Varianzhomogenität)"
            ts, pv, dfv = tsu, pvu, dfu
            se_used = seu
    else:
        tn = "Welch-t-Test"
        ts, pv, dfv = tsu, pvu, dfu
        se_used = seu

    # Cohen's d
    dfp = ne1 + ne2 - 2
    psd = (np.sqrt(((ne1 - 1) * v1 + (ne2 - 1) * v2) / dfp)
           if dfp > 0 else np.nan)
    cd = md / psd if psd and psd > 0 else np.nan

    # KI
    if (not np.isnan(dfv) and dfv > 0
            and se_used and se_used > 0):
        tc = stats.t.ppf(0.975, dfv)
        cil, ciu = md - tc * se_used, md + tc * se_used
    else:
        cil = ciu = np.nan

    sig = _sig_stars(pv)

    rows = [
        {"Statistik": "Test",
         "Wert": tn, "Entscheidung": "---"},
        {"Statistik": "t-Statistik",
         "Wert": (f"{ts:.6f}" if not np.isnan(ts) else "NaN"),
         "Entscheidung": "---"},
        {"Statistik": "p-Wert",
         "Wert": _format_p(pv), "Entscheidung": sig},
        {"Statistik": "df",
         "Wert": (f"{dfv:.4f}" if not np.isnan(dfv) else "NaN"),
         "Entscheidung": "---"},
        {"Statistik": "Mittelwert G1",
         "Wert": f"{mn1:.6f}", "Entscheidung": "---"},
        {"Statistik": "Mittelwert G2",
         "Wert": f"{mn2:.6f}", "Entscheidung": "---"},
        {"Statistik": "Differenz (G1-G2)",
         "Wert": f"{md:.6f}", "Entscheidung": "---"},
        {"Statistik": "95%-KI unten",
         "Wert": (f"{cil:.6f}" if not np.isnan(cil) else "NaN"),
         "Entscheidung": "---"},
        {"Statistik": "95%-KI oben",
         "Wert": (f"{ciu:.6f}" if not np.isnan(ciu) else "NaN"),
         "Entscheidung": "---"},
        {"Statistik": "Varianz G1",
         "Wert": f"{v1:.6f}", "Entscheidung": "---"},
        {"Statistik": "Varianz G2",
         "Wert": f"{v2:.6f}", "Entscheidung": "---"},
        {"Statistik": "Cohen's d",
         "Wert": (f"{cd:.4f}" if not np.isnan(cd) else "NaN"),
         "Entscheidung": "---"},
        {"Statistik": "n G1 (roh)",
         "Wert": n1r, "Entscheidung": "---"},
        {"Statistik": "n G2 (roh)",
         "Wert": n2r, "Entscheidung": "---"},
        {"Statistik": "n G1 (eff)",
         "Wert": f"{ne1:.2f}", "Entscheidung": "---"},
        {"Statistik": "n G2 (eff)",
         "Wert": f"{ne2:.2f}", "Entscheidung": "---"},
        {"Statistik": "Levene p",
         "Wert": lpf, "Entscheidung": dec},
        {"Statistik": "Gruppe 1",
         "Wert": g1, "Entscheidung": "---"},
        {"Statistik": "Gruppe 2",
         "Wert": g2, "Entscheidung": "---"},
        {"Statistik": "Abhängige Variable",
         "Wert": dependent, "Entscheidung": "---"},
    ]

    return StatResult(
        stat=pd.DataFrame(rows),
        test_name=f"T-Test: {dependent} nach {group} ({g1} vs. {g2})",
        info={
            "Test": tn, "Gruppen": f"{g1} vs. {g2}", "AV": dependent,
            "Gewichtung": wc or ("pd.Series" if hw else "keine")
        }
    )


# ===============================================================
# regress – OLS-Regression mit Beta
# ===============================================================

def regress(formula, data, weight=None, robust=False, show_beta=True,
            show_ci=True, show_vif=True):
    """
    OLS-Regression mit standardisierten Beta-Koeffizienten.

    Parameter:
        formula: str – 'y ~ x1 + x2 + ...'
            Unterstützt: C(x) für kategorial, x1:x2 für Interaktionen
        data: pd.DataFrame
        weight: str (Spaltenname) oder None
        robust: bool – robuste SE HC3 (default: False)
        show_beta: bool – Beta anzeigen (default: True)
        show_ci: bool – 95%-KI (default: True)
        show_vif: bool – VIF (default: True)

    Rückgabe:
        StatResult mit:
            result['stat']            → Koeffiziententabelle
            result['model']           → statsmodels-Objekt
            result['anova']           → ANOVA (wenn verfügbar)
            result.summary()          → Formatierte Ausgabe
            result['model'].summary() → Original statsmodels-Output

    Beispiel:
        regress('inc ~ sex + educ', data=df).summary()
        regress('inc ~ sex + educ', data=df, weight='w').summary()
        regress('inc ~ C(educ) + age', data=df).summary()
        regress('inc ~ sex + educ', data=df, robust=True).summary()
    """
    if not STATSMODELS_AVAILABLE:
        raise ImportError(
            "statsmodels nicht installiert: pip install statsmodels"
        )

    if '~' not in formula:
        raise ValueError(
            "Format: 'y ~ x1 + x2 + ...'\n"
            "Beispiel: regress('inc ~ sex + educ', data=df)"
        )

    y_var = formula.strip().split('~')[0].strip()
    if y_var not in data.columns:
        raise ValueError(
            f"AV '{y_var}' nicht gefunden. "
            f"Vorhanden: {list(data.columns)[:20]}"
        )

    wc = None
    if isinstance(weight, str) and weight is not None:
        if weight not in data.columns:
            raise ValueError(
                f"Gewichtungsspalte '{weight}' nicht gefunden."
            )
        wc = weight

    n_orig = len(data)

    try:
        if wc:
            model = smf.wls(
                formula, data=data, weights=data[wc]
            ).fit()
            method = f"WLS (Gewichtung: {wc})"
        elif robust:
            model = smf.ols(formula, data=data).fit(cov_type='HC3')
            method = "OLS (robuste SE, HC3)"
        else:
            model = smf.ols(formula, data=data).fit()
            method = "OLS"
    except Exception as e:
        raise ValueError(f"Modellfehler: {e}")

    # Betas
    betas = {}
    if show_beta:
        betas = _calculate_betas(model, data, formula, wc)

    # VIF
    vif_vals = {}
    if show_vif:
        vif_vals = _calculate_vif(model)

    # Koeffiziententabelle
    conf_int = model.conf_int()
    rows = []
    for name in model.params.index:
        b = model.params[name]
        se = model.bse[name]
        t = model.tvalues[name]
        p = model.pvalues[name]
        row = {
            "Variable": name,
            "b": f"{b:.4f}",
            "SE": f"{se:.4f}"
        }
        if show_beta:
            bv = betas.get(name, np.nan)
            row["Beta (β)"] = (
                f"{bv:.4f}" if isinstance(bv, float)
                and not np.isnan(bv) else "---"
            )
        row["t"] = f"{t:.4f}"
        row["p-Wert"] = _format_p(p)
        row["Sig."] = _sig_stars(p)
        if show_ci:
            idx = model.params.index.get_loc(name)
            row["95%-KI unten"] = f"{conf_int.iloc[idx, 0]:.4f}"
            row["95%-KI oben"] = f"{conf_int.iloc[idx, 1]:.4f}"
        if show_vif:
            vif = vif_vals.get(name, np.nan)
            if name == 'Intercept':
                row["VIF"] = "---"
            elif not np.isnan(vif):
                flag = (" ⚠️" if vif > 5
                        else (" 🔴" if vif > 10 else ""))
                row["VIF"] = f"{vif:.2f}{flag}"
            else:
                row["VIF"] = "---"
        rows.append(row)

    stat_df = pd.DataFrame(rows)

    # ANOVA
    try:
        anova_tbl = sm.stats.anova_lm(model, typ=2).round(4)
    except Exception:
        anova_tbl = None

    tables = {"model": model}
    if anova_tbl is not None:
        tables["anova"] = anova_tbl

    info = {
        "Formel": formula,
        "Methode": method,
        "n (verwendet)": int(model.nobs),
        "n (original)": n_orig,
        "n (entfernt)": n_orig - int(model.nobs),
        "R²": round(model.rsquared, 4),
        "R² (adj.)": round(model.rsquared_adj, 4),
        "F": (f"{model.fvalue:.4f}"
              if not np.isnan(model.fvalue) else "NaN"),
        "F p-Wert": _format_p(model.f_pvalue),
        "F Sig.": _sig_stars(model.f_pvalue),
        "AIC": round(model.aic, 2),
        "BIC": round(model.bic, 2),
        "Durbin-Watson": round(_durbin_watson(model.resid), 4),
    }
    if wc:
        info["Gewichtung"] = wc
    if robust:
        info["Robuste SE"] = "HC3"

    return StatResult(
        tables=tables, stat=stat_df,
        test_name=f"Regression: {formula}",
        info=info
    )


def _calculate_betas(model, data, formula, weight_col=None):
    betas = {}
    y_var = formula.strip().split('~')[0].strip()
    y_vals = model.model.endog

    if weight_col and weight_col in data.columns:
        try:
            w = data.loc[
                model.model.data.row_labels, weight_col
            ].values.astype(float)
        except Exception:
            w = None
    else:
        w = None

    sd_y = (_weighted_std(y_vals, w) if w is not None
            else np.std(y_vals, ddof=1))
    if sd_y == 0 or np.isnan(sd_y):
        return {n: np.nan for n in model.params.index}

    for name in model.params.index:
        if name == 'Intercept':
            betas[name] = np.nan
            continue
        b = model.params[name]
        try:
            idx = model.model.exog_names.index(name)
            x_vals = model.model.exog[:, idx]
            sd_x = (_weighted_std(x_vals, w) if w is not None
                    else np.std(x_vals, ddof=1))
            betas[name] = b * (sd_x / sd_y) if sd_x > 0 else np.nan
        except (ValueError, IndexError):
            betas[name] = np.nan
    return betas


def _calculate_vif(model):
    vif_vals = {}
    try:
        exog = model.model.exog
        names = model.model.exog_names
        for i, name in enumerate(names):
            if name == 'Intercept':
                continue
            try:
                vif_vals[name] = variance_inflation_factor(exog, i)
            except Exception:
                vif_vals[name] = np.nan
    except Exception:
        pass
    return vif_vals


# ===============================================================
# beta – Standardisierte Regressionskoeffizienten
# ===============================================================

def beta(formula, data, weight=None, full=False):
    """
    Standardisierte Regressionskoeffizienten (β).

    Parameter:
        formula: str – 'y ~ x1 + x2 + ...'
        data: pd.DataFrame
        weight: str oder pd.Series (optional)
        full: bool – vollständige Tabelle (default: False)

    Rückgabe:
        pd.Series (full=False) oder StatResult (full=True)

    Beispiel:
        beta('inc ~ age + educ', data=df)
        beta('inc ~ age + educ', data=df, full=True).summary()
    """
    parts = formula.strip().split('~')
    if len(parts) != 2:
        raise ValueError("Format: 'y ~ x1 + x2 + ...'")

    y_var = parts[0].strip()
    x_vars = [v.strip() for v in parts[1].split('+')]
    all_vars = [y_var] + x_vars

    missing = [v for v in all_vars if v not in data.columns]
    if missing:
        raise ValueError(f"Variablen fehlen: {missing}")

    wc = None
    if isinstance(weight, str) and weight is not None:
        if weight not in data.columns:
            raise ValueError(
                f"Gewichtungsspalte '{weight}' nicht gefunden."
            )
        wc = weight

    cols = list(all_vars)
    if wc and wc not in cols:
        cols.append(wc)

    dc = data[cols].dropna()
    if dc.empty:
        raise ValueError("Keine Daten nach NaN-Entfernung.")
    if len(dc) < len(x_vars) + 1:
        raise ValueError(
            f"Zu wenig Beobachtungen ({len(dc)}) "
            f"für {len(x_vars)} Prädiktoren."
        )

    for v in all_vars:
        if dc[v].nunique() < 2:
            raise ValueError(f"Variable '{v}' hat nur einen Wert.")

    w = (dc[wc].values.astype(float) if wc
         else (weight.loc[dc.index].values.astype(float)
               if isinstance(weight, pd.Series) else None))

    corr = (_weighted_corr(dc[all_vars], w) if w is not None
            else dc[all_vars].corr())

    if corr.isna().any().any():
        raise ValueError("Korrelationsmatrix enthält NaN.")

    R = corr.loc[x_vars, x_vars].values
    r_yx = corr.loc[y_var, x_vars].values

    try:
        bc = np.linalg.solve(R, r_yx)
    except np.linalg.LinAlgError:
        raise ValueError(
            "Korrelationsmatrix singulär (Multikollinearität)."
        )

    r_sq = float(r_yx @ bc)
    n = len(dc)
    k = len(x_vars)
    ne = _effective_sample_size(w) if w is not None else float(n)
    r_sq_adj = (1 - (1 - r_sq) * (ne - 1) / (ne - k - 1)
                if ne > k + 1 else np.nan)

    if not full:
        result = pd.Series(bc, index=x_vars, name='beta')
        result.attrs['R_squared'] = r_sq
        result.attrs['R_squared_adj'] = r_sq_adj
        result.attrs['n'] = n
        result.attrs['n_eff'] = ne
        return result

    mse = (1 - r_sq) / (ne - k - 1) if ne > k + 1 else np.nan
    try:
        Ri = np.linalg.inv(R)
        se_b = np.sqrt(mse * np.diag(Ri))
    except:
        se_b = np.full(k, np.nan)

    t_vals = bc / se_b
    df_r = ne - k - 1
    p_vals = [
        (2 * (1 - stats.t.cdf(abs(t), df_r))
         if not np.isnan(t) and df_r > 0 else np.nan)
        for t in t_vals
    ]

    f_stat = ((r_sq / k) / ((1 - r_sq) / df_r)
              if df_r > 0 and k > 0 else np.nan)
    p_f = (1 - stats.f.cdf(f_stat, k, df_r)
           if not np.isnan(f_stat) else np.nan)

    rows = []
    for i, v in enumerate(x_vars):
        rows.append({
            "Variable": v,
            "Beta (β)": f"{bc[i]:.4f}",
            "SE (β)": (f"{se_b[i]:.4f}"
                       if not np.isnan(se_b[i]) else "NaN"),
            "t": (f"{t_vals[i]:.4f}"
                  if not np.isnan(t_vals[i]) else "NaN"),
            "p-Wert": _format_p(p_vals[i]),
            "Sig.": _sig_stars(p_vals[i]),
            "r(y,x)": f"{r_yx[i]:.4f}"
        })

    return StatResult(
        stat=pd.DataFrame(rows),
        test_name=f"Standardisierte Regression: {formula}",
        info={
            "Formel": formula,
            "n": n,
            "n (eff)": round(ne, 2),
            "R²": round(r_sq, 4),
            "R² (adj.)": (round(r_sq_adj, 4)
                          if not np.isnan(r_sq_adj) else "NaN"),
            "F": (f"{f_stat:.4f}"
                  if not np.isnan(f_stat) else "NaN"),
            "F p": _format_p(p_f),
            "F Sig.": _sig_stars(p_f),
            "Gewichtung": (wc or ("pd.Series" if w is not None
                                  else "keine"))
        }
    )


# ===============================================================
# cronbach – Reliabilitätsanalyse
# ===============================================================

def cronbach(df, items, weight=None, item_analysis=True):
    """
    Cronbach's Alpha und Item-Analyse.

    Parameter:
        df: pd.DataFrame
        items: list – Spaltennamen der Items
        weight: str oder pd.Series (optional) – derzeit nur ungewichtet
        item_analysis: bool – Item-Total-Korrelationen (default: True)

    Rückgabe:
        StatResult

    Beispiel:
        cronbach(df, ['item1', 'item2', 'item3', 'item4']).summary()
    """
    missing_items = [i for i in items if i not in df.columns]
    if missing_items:
        raise ValueError(
            f"Items nicht gefunden: {missing_items}. "
            f"Vorhanden: {list(df.columns)[:20]}"
        )

    di = df[items].dropna()
    n = len(di)
    k = len(items)

    if n < 2:
        raise ValueError("Zu wenig gültige Fälle.")
    if k < 2:
        raise ValueError("Mindestens 2 Items benötigt.")

    iv = di.var(ddof=1)
    tv = di.sum(axis=1).var(ddof=1)
    alpha = ((k / (k - 1)) * (1 - iv.sum() / tv)
             if tv > 0 else np.nan)

    if alpha >= 0.9:
        rating = "exzellent"
    elif alpha >= 0.8:
        rating = "gut"
    elif alpha >= 0.7:
        rating = "akzeptabel"
    elif alpha >= 0.6:
        rating = "fragwürdig"
    elif alpha >= 0.5:
        rating = "schlecht"
    else:
        rating = "inakzeptabel"

    info = {
        "Cronbach's Alpha": round(alpha, 4),
        "Bewertung": rating,
        "Items": k,
        "n (Listwise)": n,
        "n (entfernt)": len(df) - n
    }

    stat_df = None
    if item_analysis:
        ts = di.sum(axis=1)
        rows = []
        for item in items:
            rs = ts - di[item]
            rit = di[item].corr(rs)
            rem = [i for i in items if i != item]
            if len(rem) >= 2:
                rv = di[rem].var(ddof=1)
                rtv = di[rem].sum(axis=1).var(ddof=1)
                kr = len(rem)
                air = ((kr / (kr - 1)) * (1 - rv.sum() / rtv)
                       if rtv > 0 else np.nan)
            else:
                air = np.nan
            rec = ("⚠️ entfernen" if rit < 0.2
                   else ("prüfen" if rit < 0.3 else "✅ ok"))
            rows.append({
                "Item": item,
                "M": f"{di[item].mean():.2f}",
                "SD": f"{di[item].std():.2f}",
                "r(it)": f"{rit:.4f}",
                "Alpha ohne": (f"{air:.4f}"
                               if not np.isnan(air) else "NaN"),
                "Empfehlung": rec
            })
        stat_df = pd.DataFrame(rows)

    return StatResult(
        stat=stat_df,
        test_name=f"Reliabilitätsanalyse ({k} Items)",
        info=info
    )


# ===============================================================
# effect_size – Effektstärken-Rechner
# ===============================================================

def effect_size(test_type, **kwargs):
    """
    Berechnet gängige Effektstärken.

    Parameter:
        test_type: str
            'cohen_d'    → aus m1, m2, sd1, sd2 (optional: n1, n2)
            'eta_sq'     → aus f, df1, df2
            'omega_sq'   → aus f, df1, df2, n
            'r_to_d'     → konvertiert r in d
            'd_to_r'     → konvertiert d in r
            'odds_ratio' → aus a, b, c, d (2×2-Tabelle)

    Rückgabe:
        StatResult

    Beispiel:
        effect_size('cohen_d', m1=50, m2=45, sd1=10, sd2=12)
        effect_size('eta_sq', f=4.5, df1=2, df2=97)
        effect_size('r_to_d', r=0.3)
        effect_size('d_to_r', d=0.5)
        effect_size('odds_ratio', a=30, b=10, c=20, d=40)
    """
    rows = []

    if test_type == 'cohen_d':
        m1, m2 = kwargs['m1'], kwargs['m2']
        sd1, sd2 = kwargs['sd1'], kwargs['sd2']
        n1, n2 = kwargs.get('n1'), kwargs.get('n2')
        if n1 and n2:
            psd = np.sqrt(
                ((n1 - 1) * sd1 ** 2 + (n2 - 1) * sd2 ** 2)
                / (n1 + n2 - 2)
            )
        else:
            psd = np.sqrt((sd1 ** 2 + sd2 ** 2) / 2)
        d = (m1 - m2) / psd if psd > 0 else np.nan
        rat = ("groß" if abs(d) >= 0.8
               else ("mittel" if abs(d) >= 0.5
                     else ("klein" if abs(d) >= 0.2
                           else "vernachlässigbar")))
        rows.append({
            "Maß": "Cohen's d",
            "Wert": f"{d:.4f}",
            "Bewertung": rat
        })

        # Zusätzlich: r aus d
        r_from_d = d / np.sqrt(d ** 2 + 4)
        rows.append({
            "Maß": "r (aus d)",
            "Wert": f"{r_from_d:.4f}",
            "Bewertung": "---"
        })

    elif test_type == 'eta_sq':
        f, df1, df2 = kwargs['f'], kwargs['df1'], kwargs['df2']
        eta = (f * df1) / (f * df1 + df2)
        rat = ("groß" if eta >= 0.14
               else ("mittel" if eta >= 0.06
                     else ("klein" if eta >= 0.01
                           else "vernachlässigbar")))
        rows.append({
            "Maß": "η² (Eta²)",
            "Wert": f"{eta:.4f}",
            "Bewertung": rat
        })

    elif test_type == 'omega_sq':
        f, df1, df2 = kwargs['f'], kwargs['df1'], kwargs['df2']
        n = kwargs.get('n', df1 + df2 + 1)
        omega = ((f * df1 - df1) / (f * df1 + df2 + 1)
                 if (f * df1 + df2 + 1) > 0 else np.nan)
        rat = ("groß" if omega >= 0.14
               else ("mittel" if omega >= 0.06
                     else ("klein" if omega >= 0.01
                           else "vernachlässigbar")))
        rows.append({
            "Maß": "ω² (Omega²)",
            "Wert": f"{omega:.4f}",
            "Bewertung": rat
        })

    elif test_type == 'r_to_d':
        r = kwargs['r']
        d = (2 * r / np.sqrt(1 - r ** 2)
             if abs(r) < 1 else np.nan)
        rows.append({
            "Maß": "r → d",
            "Wert": (f"{d:.4f}" if not np.isnan(d) else "NaN"),
            "Bewertung": f"r = {r:.4f}"
        })

    elif test_type == 'd_to_r':
        d = kwargs['d']
        r = d / np.sqrt(d ** 2 + 4)
        rows.append({
            "Maß": "d → r",
            "Wert": f"{r:.4f}",
            "Bewertung": f"d = {d:.4f}"
        })

    elif test_type == 'odds_ratio':
        a, b, c, d_val = (kwargs['a'], kwargs['b'],
                          kwargs['c'], kwargs['d'])
        od = ((a * d_val) / (b * c)
              if (b * c) > 0 else np.nan)
        log_or = np.log(od) if od and od > 0 else np.nan
        se_log = (np.sqrt(1 / a + 1 / b + 1 / c + 1 / d_val)
                  if all(v > 0 for v in [a, b, c, d_val])
                  else np.nan)
        ci_low = (np.exp(log_or - 1.96 * se_log)
                  if not np.isnan(se_log) else np.nan)
        ci_high = (np.exp(log_or + 1.96 * se_log)
                   if not np.isnan(se_log) else np.nan)
        rows.append({
            "Maß": "Odds Ratio",
            "Wert": (f"{od:.4f}" if not np.isnan(od) else "NaN"),
            "Bewertung": "---"
        })
        rows.append({
            "Maß": "95%-KI unten",
            "Wert": (f"{ci_low:.4f}"
                     if not np.isnan(ci_low) else "NaN"),
            "Bewertung": "---"
        })
        rows.append({
            "Maß": "95%-KI oben",
            "Wert": (f"{ci_high:.4f}"
                     if not np.isnan(ci_high) else "NaN"),
            "Bewertung": "---"
        })
        rows.append({
            "Maß": "ln(OR)",
            "Wert": (f"{log_or:.4f}"
                     if not np.isnan(log_or) else "NaN"),
            "Bewertung": "---"
        })

    else:
        raise ValueError(
            f"Unbekannt: '{test_type}'. Erlaubt: 'cohen_d', 'eta_sq', "
            f"'omega_sq', 'r_to_d', 'd_to_r', 'odds_ratio'"
        )

    return StatResult(
        stat=pd.DataFrame(rows),
        test_name=f"Effektstärke: {test_type}",
        info=kwargs
    )


# ===============================================================
# normality_test – Normalverteilungstests
# ===============================================================

def normality_test(df, column):
    """
    Normalverteilungstests.

    Tests: Shapiro-Wilk (n<5000), Kolmogorov-Smirnov, Schiefe/Kurtosis.

    Parameter:
        df: pd.DataFrame
        column: str

    Rückgabe:
        StatResult

    Beispiel:
        normality_test(df, 'inc').summary()
    """
    from scipy.stats import shapiro, kstest

    if column not in df.columns:
        raise ValueError(f"Spalte '{column}' nicht gefunden.")

    data = pd.to_numeric(df[column], errors='coerce').dropna()
    n = len(data)

    if n < 3:
        raise ValueError(
            f"Zu wenig Werte ({n}). Mindestens 3 benötigt."
        )

    rows = []

    if n < 5000:
        sw_stat, sw_p = shapiro(data)
        rows.append({
            "Test": "Shapiro-Wilk",
            "Statistik": f"{sw_stat:.4f}",
            "p-Wert": _format_p(sw_p),
            "Sig.": _sig_stars(sw_p),
            "Ergebnis": ("normalverteilt" if sw_p > 0.05
                         else "NICHT normalverteilt")
        })
    else:
        rows.append({
            "Test": "Shapiro-Wilk",
            "Statistik": "---",
            "p-Wert": "---",
            "Sig.": "",
            "Ergebnis": f"n={n} > 5000, Test nicht geeignet"
        })

    ks_stat, ks_p = kstest(data, 'norm',
                           args=(data.mean(), data.std()))
    rows.append({
        "Test": "Kolmogorov-Smirnov",
        "Statistik": f"{ks_stat:.4f}",
        "p-Wert": _format_p(ks_p),
        "Sig.": _sig_stars(ks_p),
        "Ergebnis": ("normalverteilt" if ks_p > 0.05
                     else "NICHT normalverteilt")
    })

    skew = data.skew()
    kurt = data.kurtosis()
    se_s = np.sqrt(6 / n)
    se_k = np.sqrt(24 / n)
    z_s = skew / se_s
    z_k = kurt / se_k

    rows.append({
        "Test": f"Schiefe (z={z_s:.2f})",
        "Statistik": f"{skew:.4f}",
        "p-Wert": "---",
        "Sig.": "⚠️" if abs(z_s) > 1.96 else "✅",
        "Ergebnis": ("symmetrisch" if abs(z_s) <= 1.96
                     else "schief")
    })
    rows.append({
        "Test": f"Kurtosis (z={z_k:.2f})",
        "Statistik": f"{kurt:.4f}",
        "p-Wert": "---",
        "Sig.": "⚠️" if abs(z_k) > 1.96 else "✅",
        "Ergebnis": ("mesokurtisch" if abs(z_k) <= 1.96
                     else "nicht mesokurtisch")
    })

    return StatResult(
        stat=pd.DataFrame(rows),
        test_name=f"Normalverteilungstests: {column}",
        info={
            "Variable": column,
            "n": n,
            "M": round(data.mean(), 4),
            "SD": round(data.std(), 4)
        }
    )


# ===============================================================
# compare_groups – Deskriptiver Gruppenvergleich
# ===============================================================

def compare_groups(df, group, variables, weight=None):
    """
    Vergleicht Mittelwerte mehrerer Variablen über Gruppen.

    Parameter:
        df: pd.DataFrame
        group: str – Gruppenvariable
        variables: list – Variablennamen
        weight: str oder pd.Series (optional)

    Rückgabe:
        StatResult

    Beispiel:
        compare_groups(df, 'sex', ['inc', 'age', 'educ']).summary()
    """
    if group not in df.columns:
        raise ValueError(
            f"Gruppenvariable '{group}' nicht gefunden."
        )
    for v in variables:
        if v not in df.columns:
            raise ValueError(f"Variable '{v}' nicht gefunden.")

    groups = sorted(df[group].dropna().unique())

    rows = []
    for var in variables:
        row = {"Variable": var}
        for g in groups:
            mask = df[group] == g
            data = pd.to_numeric(
                df.loc[mask, var], errors='coerce'
            ).dropna()

            if weight is not None:
                try:
                    ws = _validate_weight(weight, df.loc[mask])
                    if ws is not None:
                        wv = ws.loc[data.index]
                        m = _weighted_mean(data, wv)
                        s = _weighted_std(data, wv)
                    else:
                        m, s = data.mean(), data.std()
                except Exception:
                    m, s = data.mean(), data.std()
            else:
                m, s = data.mean(), data.std()

            row[f"M ({g})"] = f"{m:.2f}"
            row[f"SD ({g})"] = f"{s:.2f}"
            row[f"n ({g})"] = len(data)
        rows.append(row)

    return StatResult(
        stat=pd.DataFrame(rows),
        test_name=f"Gruppenvergleich nach {group}",
        info={
            "Gruppenvariable": group,
            "Gruppen": list(groups),
            "Variablen": variables
        }
    )


# ===============================================================
# export_results – Ergebnisse exportieren
# ===============================================================

def export_results(result, filename, format='excel', decimal=','):
    """
    Exportiert Ergebnisse in eine Datei.

    Parameter:
        result: StatResult oder pd.DataFrame
        filename: str – Dateiname (ohne Endung)
        format: 'excel', 'csv', 'html', 'latex' (default: 'excel')
        decimal: str – Dezimaltrennzeichen (default: ',')

    Beispiel:
        export_results(result, 'ergebnis')
        export_results(result, 'ergebnis', format='latex')
    """
    if isinstance(result, StatResult):
        dfs = {}
        if result.stat is not None:
            dfs['Statistiken'] = result.stat
        for name, table in result.tables.items():
            if isinstance(table, pd.DataFrame):
                dfs[name] = table
            elif isinstance(table, StatResult) and table.stat is not None:
                dfs[name] = table.stat
        if result.info:
            dfs['Info'] = pd.DataFrame(
                list(result.info.items()),
                columns=['Eigenschaft', 'Wert']
            )
    elif isinstance(result, pd.DataFrame):
        dfs = {'Ergebnis': result}
    else:
        raise TypeError(
            "result muss StatResult oder pd.DataFrame sein."
        )

    if not dfs:
        print("⚠️ Keine exportierbaren Tabellen gefunden.")
        return

    if format == 'excel':
        fp = f"{filename}.xlsx"
        try:
            with pd.ExcelWriter(fp, engine='openpyxl') as writer:
                for sheet, df_exp in dfs.items():
                    df_exp.to_excel(
                        writer,
                        sheet_name=str(sheet)[:31],
                        index=False
                    )
            print(f"✅ Exportiert: {fp} ({len(dfs)} Sheets)")
        except ImportError:
            print(
                "⚠️ openpyxl nicht installiert: pip install openpyxl"
            )

    elif format == 'csv':
        for name, df_exp in dfs.items():
            fp = f"{filename}_{name}.csv"
            df_exp.to_csv(fp, index=False, sep=';', decimal=decimal)
            print(f"✅ Exportiert: {fp}")

    elif format == 'html':
        fp = f"{filename}.html"
        title = (result.test_name if isinstance(result, StatResult)
                 else 'Ergebnis')
        html = (
            f"<html><head><meta charset='utf-8'>"
            f"<title>{title}</title></head><body>\n"
        )
        html += f"<h1>{title}</h1>\n"
        for name, df_exp in dfs.items():
            html += (
                f"<h2>{name}</h2>\n"
                f"{df_exp.to_html(index=False)}\n"
            )
        html += "</body></html>"
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Exportiert: {fp}")

    elif format == 'latex':
        fp = f"{filename}.tex"
        latex = ""
        for name, df_exp in dfs.items():
            latex += (
                f"% {name}\n"
                f"{df_exp.to_latex(index=False)}\n\n"
            )
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(latex)
        print(f"✅ Exportiert: {fp}")

    else:
        raise ValueError(
            f"Unbekanntes Format: '{format}'. "
            f"Erlaubt: 'excel', 'csv', 'html', 'latex'"
        )


# ===============================================================
# create_dummies
# ===============================================================

def create_dummies(df, column, prefix=None):
    """
    Erstellt Dummy-Variablen.

    Beispiel:
        df = create_dummies(df, 'educ', prefix='educ')
    """
    if column not in df.columns:
        raise ValueError(f"Spalte '{column}' nicht gefunden.")
    df = df.copy()
    col_data = pd.to_numeric(
        df[column], errors='coerce'
    ).dropna().astype(int)
    dummies = pd.get_dummies(
        col_data, prefix=prefix or column, dtype=int
    )
    return pd.concat([df, dummies], axis=1)


# ===============================================================
# help_cheatstat
# ===============================================================

def help_cheatstat():
    """Kurzanleitung für alle Funktionen."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  cheatstat v4.1 – Kurzanleitung                             ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  FEHLENDE WERTE:                                             ║
    ║    missing_report(df).summary()                              ║
    ║                                                              ║
    ║  UMKODIEREN:                                                 ║
    ║    df = recode(df, 'var', {'1,2': 1, '3-6': 2, '>6': 3})   ║
    ║    df = recode(df, 'var', {'>=5 and <=10': 1, 'else': 0})  ║
    ║    df = recode(df, 'var', {'not 1,2': np.nan},              ║
    ║                new_name='var_clean')                         ║
    ║                                                              ║
    ║  HÄUFIGKEITEN:                                               ║
    ║    fre(df, 'var')                                            ║
    ║    fre(df, 'var', weight='gewicht')                          ║
    ║    fre_wl(df, 'var', dfL)                                    ║
    ║    fre_wl(df, 'var', dfL, weight='gewicht')                  ║
    ║                                                              ║
    ║  DESKRIPTIVE STATISTIK:                                      ║
    ║    uniV(df, 'var').summary()                                 ║
    ║    uniV(df, 'var', weight='w').summary()                     ║
    ║                                                              ║
    ║  KREUZTABELLE:                                               ║
    ║    cross_tab(df, 'v1', 'v2').summary(show_tables=True)      ║
    ║                                                              ║
    ║  ZUSAMMENHANG (bivariat):                                    ║
    ║    biV(df, 'x', 'y', 'nominal').summary()                   ║
    ║    biV(df, 'x', 'y', 'ordinal').summary()                   ║
    ║                                                              ║
    ║  T-TEST:                                                     ║
    ║    ttest_u(group='sex', g1=1, g2=2,                          ║
    ║            dependent='inc', data=df).summary()               ║
    ║                                                              ║
    ║  REGRESSION (OLS mit Beta):                                  ║
    ║    regress('y ~ x1 + x2', data=df).summary()                ║
    ║    regress('y ~ C(educ) + age', data=df).summary()           ║
    ║    regress('y ~ x1 + x2', data=df, weight='w').summary()    ║
    ║    regress('y ~ x1', data=df, robust=True).summary()        ║
    ║    result['model'].summary()  # statsmodels-Original         ║
    ║                                                              ║
    ║  BETA (nur Koeffizienten):                                   ║
    ║    beta('y ~ x1 + x2', data=df)                             ║
    ║    beta('y ~ x1 + x2', data=df, full=True).summary()        ║
    ║                                                              ║
    ║  CRONBACH'S ALPHA:                                           ║
    ║    cronbach(df, ['i1','i2','i3','i4']).summary()             ║
    ║                                                              ║
    ║  EFFEKTSTÄRKEN:                                              ║
    ║    effect_size('cohen_d', m1=50, m2=45,                      ║
    ║                sd1=10, sd2=12).summary()                     ║
    ║    effect_size('eta_sq', f=4.5, df1=2, df2=97).summary()    ║
    ║    effect_size('r_to_d', r=0.3).summary()                   ║
    ║    effect_size('d_to_r', d=0.5).summary()                   ║
    ║    effect_size('odds_ratio', a=30, b=10,                     ║
    ║                c=20, d=40).summary()                         ║
    ║                                                              ║
    ║  NORMALVERTEILUNG:                                           ║
    ║    normality_test(df, 'var').summary()                       ║
    ║                                                              ║
    ║  GRUPPENVERGLEICH (deskriptiv):                              ║
    ║    compare_groups(df, 'sex', ['inc','age']).summary()        ║
    ║                                                              ║
    ║  EXPORT:                                                     ║
    ║    export_results(result, 'dateiname')                       ║
    ║    export_results(result, 'datei', format='latex')           ║
    ║    export_results(result, 'datei', format='html')            ║
    ║                                                              ║
    ║  DUMMY-VARIABLEN:                                            ║
    ║    df = create_dummies(df, 'educ', prefix='educ')            ║
    ║                                                              ║
    ║  SIGNIFIKANZSTERNE:                                          ║
    ║    *** p < .001  |  ** p < .01  |  * p < .05  |  n.s.       ║
    ║                                                              ║
    ║  ERGEBNISSE ABRUFEN:                                         ║
    ║    result.summary()                     # Übersicht          ║
    ║    result.summary(show_tables=True)     # mit Tabellen       ║
    ║    result['stat']                       # Statistik-Tabelle  ║
    ║    result.keys()                        # Alle Schlüssel     ║
    ║                                                              ║
    ║  HILFE:                                                      ║
    ║    help_cheatstat()                                          ║
    ║    help(regress)                                             ║
    ╚══════════════════════════════════════════════════════════════╝
    """)


# ===============================================================
# Exportliste
# ===============================================================

__all__ = [
    'missing_report',
    'recode',
    'fre',
    'fre_wl',
    'uniV',
    'biV',
    'cross_tab',
    'ttest_u',
    'regress',
    'beta',
    'cronbach',
    'effect_size',
    'normality_test',
    'compare_groups',
    'export_results',
    'create_dummies',
    'help_cheatstat',
    'StatResult'
]