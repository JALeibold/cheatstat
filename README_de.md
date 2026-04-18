<div align="center">

# cheatstat

**Einfache statistische Funktionen für Sozialwissenschaftler**

[![PyPI version](https://img.shields.io/pypi/v/cheatstat?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/cheatstat/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![statsmodels](https://img.shields.io/badge/statsmodels-optional-green)](https://www.statsmodels.org)
[![Documentation](https://img.shields.io/badge/Dokumentation-Deutsch-green?logo=github)](docs/de/index.md)

[🇬🇧 English Documentation](README_en.md)

</div>

---

## ⚠️ Wichtiger Hinweis zur Gewichtung

> Diese Implementierung ist eine **Approximation**. Für wissenschaftliche
> Publikationen muss das vollständige Survey-Design (PSU, Strata) berücksichtigt
> werden.

cheatstat bietet eine vereinfachte Gewichtung für **explorative Analysen und
Lehrzwecke**. Es berücksichtigt **nicht** das vollständige Survey-Design
(Primary Sampling Units, Strata).

| cheatstat ist **nicht** für | cheatstat ist **ideal** für |
|------------------------------|------------------------------|
| Offizielle statistische Berichte | Lehrveranstaltungen in den Sozialwissenschaften |
| Wissenschaftliche Publikationen | Explorative Datenanalyse |
| Politische Entscheidungsgrundlagen | Schnelle Überprüfung von Hypothesen |
| | Einstieg in statistische Methoden |

**Für wissenschaftliche Publikationen verwenden Sie:**
`survey` (R) · `SURVEYMEANS` (SAS) · *Complex Samples* (SPSS)

---

## Inhaltsverzeichnis

- [Installation](#installation)
- [Erste Schritte](#erste-schritte)
- [Funktionsübersicht](#funktionsübersicht)
- [ALLBUS-Beispiele](#allbus-beispiele)
- [Ergebnisse abrufen](#ergebnisse-abrufen)
- [Dokumentation](#dokumentation)
- [Abhängigkeiten](#abhängigkeiten)
- [Lizenz](#lizenz)

---

## Installation

```bash
# Basisinstallation
pip install cheatstat

# Empfohlen: mit OLS-Regression
pip install cheatstat statsmodels

# Vollständig: mit allen optionalen Paketen
pip install cheatstat statsmodels numba openpyxl pyreadstat
```

---

## Erste Schritte

```python
import cheatstat as cs
import pandas as pd

# ALLBUS-Daten laden
A18N = pd.read_spss('ALLBUS2018.sav',
    usecols=["sex", "inc", "eastwest", "iscd11", "pv19", "wghtpew"],
    convert_categoricals=False)

A18L = pd.read_spss('ALLBUS2018.sav',
    usecols=["sex", "inc", "eastwest", "iscd11", "pv19", "wghtpew"],
    convert_categoricals=True)

# Kurzanleitung anzeigen
cs.help_cheatstat()
```

---

## Funktionsübersicht

| Funktion | Beschreibung |
|----------|-------------|
| `missing_report(df)` | Fehlende-Werte-Analyse |
| `recode(df, col, mapping)` | Variablen umkodieren |
| `fre(df, col)` | Häufigkeitstabelle |
| `fre_wl(df, col, labels)` | Häufigkeitstabelle mit Wertelabels |
| `uniV(df, col)` | Univariate Analyse |
| `cross_tab(df, col1, col2)` | Kreuztabelle |
| `biV(df, col1, col2, scale)` | Bivariate Analyse |
| `ttest_u(group, g1, g2, dependent, data)` | Unabhängiger t-Test |
| `regress(formula, data)` | OLS-Regression mit Beta-Koeffizienten |
| `beta(formula, data)` | Standardisierte Koeffizienten |
| `cronbach(df, items)` | Reliabilitätsanalyse (Cronbach's Alpha) |
| `effect_size(type, ...)` | Effektstärken-Rechner |
| `normality_test(df, col)` | Normalverteilungstests |
| `compare_groups(df, group, vars)` | Deskriptiver Gruppenvergleich |
| `export_results(result, file)` | Ergebnisse exportieren |
| `create_dummies(df, col)` | Dummy-Variablen erstellen |
| `help_cheatstat()` | Kurzanleitung |

---

## ALLBUS-Beispiele

### Fehlende Werte analysieren

```python
cs.missing_report(A18N).summary()
```

```
  Variable  n (gültig)  n (fehlend)  % fehlend Status
     scage        1916         1561      44.90      🔴
    isco08        1950         1527      43.92      🔴
       inc        3092          385      11.07      🔴
  eastwest        3477            0       0.00      ✅
       sex        3477            0       0.00      ✅
```

---

### Häufigkeitstabelle mit Labels

```python
cs.fre_wl(A18N, 'educ', A18L, sort_by_value=True)
```

```
  Ausprägung                 Label  Häufigkeiten Prozent  gültigeP
0        1.0        NO CERTIFICATE            50    1.44      1.44
1        2.0          LOWEST LEVEL           809   23.30     23.30
2        3.0    INTERMEDIARY LEVEL          1190   34.37     34.37
3        4.0  QUALI.UNIV.APPL.SCI.           301    8.69      8.69
4        5.0  QUALI.FOR UNIVERSITY          1070   30.92     30.92
```

---

### Univariate Analyse

```python
cs.uniV(A18N, 'inc').summary()
```

```
  50%-Quantil (Median)      1500.00
            Mittelwert    1825.8865
    Standardabweichung    1320.9836
               Schiefe       2.9523
```

---

### Zusammenhangsmaße (biV)

```python
# Nominal: Chi², Phi
cs.biV(A18N, "eastwest", "sex", scale="nominal").summary()
```

```
    Maß   Wert  p-Wert Sig.
   Chi² 0.1511 0.69750 n.s.
Phi (φ) 0.0066     ---     
```

```python
# Ordinal: Pearson-r, Spearman-ρ, Kendall-τ, Somers' D
cs.biV(A18N, "eastwest", "pv19", scale="ordinal").summary()
```

```
            Maß    Wert   p-Wert Sig.
      Pearson-r -0.1000 9.01e-09  ***
   Spearman-Rho -0.1015 5.36e-09  ***
Kendall's Tau-b -0.0876 5.82e-09  ***
```

---

### T-Test

```python
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N).summary()
```

```
       t-Statistik  18.274488
            p-Wert  0.00e+00   ***
 Differenz (G1-G2)  809.79 €
         Cohen's d  0.6439 (mittel)
```

```python
# Mit Survey-Gewichtung
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N, weight='wghtpew').summary()
```

```
 Differenz (G1-G2)  891.93 €
         Cohen's d  0.6928 (mittel-groß)
```

---

### Regression

```python
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N).summary()
```

```
  R²: 0.2649    F: 369.93  ***
------------------------------------------------------------
 Variable   b (€)  Beta (β)  Sig.   VIF
      sex -720.77   -0.2726  ***   1.01
 eastwest -395.87   -0.1400  ***   1.00
   iscd11 +288.15   +0.3898  ***   1.01
```

```python
# Mit Gewichtung und robusten SE
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N,
           weight='wghtpew', robust=True).summary()
```

---

### Reliabilitätsanalyse

```python
cs.cronbach(A18N, ['pr04', 'pr05', 'pr07']).summary()
```

```
  Cronbach's Alpha: -0.2415
  Bewertung: inakzeptabel
```

---

### Effektstärken

```python
cs.effect_size('cohen_d', m1=2213, m2=1403, sd1=1519, sd2=888).summary()
# → Cohen's d = 0.6439 (mittel)

cs.effect_size('r_to_d', r=0.10).summary()
# → d = 0.2010

cs.effect_size('odds_ratio', a=30, b=10, c=20, d=40).summary()
# → OR = 6.00, 95%-KI [2.25, 16.00]
```

---

### Variablen umkodieren

```python
# Bildungskategorien
A18N = cs.recode(A18N, 'educ',
    {'1,2': 1, '3,4': 2, '5': 3}, new_name='educ3')

# Alterskategorien
A18N = cs.recode(A18N, 'age',
    {'18-34': 1, '35-54': 2, '55-99': 3}, new_name='age3')

# Komplex
A18N = cs.recode(A18N, 'inc',
    {'<1000': 1, '>=1000 and <2500': 2, '>=2500': 3}, new_name='inc3')
```

---

### Export

```python
result = cs.regress('inc ~ sex + eastwest + iscd11', data=A18N)

# Excel (Standard)
cs.export_results(result, 'regression_ergebnis')

# LaTeX für Seminararbeiten
cs.export_results(result, 'regression_ergebnis', format='latex')
```

---

## Ergebnisse abrufen

Alle Funktionen geben ein `StatResult`-Objekt zurück:

```python
result = cs.regress('inc ~ sex + eastwest + iscd11', data=A18N)

result.summary()                   # Formatierte Ausgabe
result.summary(show_tables=True)   # Inkl. aller Tabellen
result['stat']                     # Koeffizienten als DataFrame
result['model']                    # statsmodels-Objekt
result['model'].summary()          # Original statsmodels-Output
result.keys()                      # Alle verfügbaren Schlüssel
```

| Schlüssel | Inhalt |
|-----------|--------|
| `'stat'` | Hauptergebnistabelle |
| `'fre'` | Häufigkeitstabelle (uniV) |
| `'observed'` | Beobachtete Häufigkeiten (cross_tab) |
| `'col_percent'` | Spaltenprozentuierung (cross_tab) |
| `'model'` | statsmodels-Objekt (regress) |
| `'anova'` | ANOVA-Tabelle (regress) |
| `'cross_tab'` | Kreuztabelle (biV) |

---

## Dokumentation

| Sprache | Inhalt |
|---------|--------|
| [📖 Deutsche Hauptdokumentation](docs/de/index.md) | Vollständige Anleitung |
| [📦 Installation](docs/de/installation.md) | pip, conda, Abhängigkeiten |
| [🚀 Grundlegende Nutzung](docs/de/usage.md) | StatResult, Tipps |
| [💡 Beispiele](docs/de/examples.md) | ALLBUS-Beispiele mit Ausgaben |
| [📋 API-Referenz](docs/de/api.md) | Alle Parameter und Rückgaben |

---

## Abhängigkeiten

### Pflicht (automatisch installiert)

| Paket | Verwendung |
|-------|-----------|
| `pandas ≥ 1.3` | Datenverarbeitung |
| `numpy ≥ 1.20` | Numerische Berechnungen |
| `scipy ≥ 1.7` | Statistische Tests |

### Optional (empfohlen)

| Paket | Wofür | Installation |
|-------|-------|-------------|
| `statsmodels` | `regress()` | `pip install statsmodels` |
| `numba` | Schnelle Berechnungen | `pip install numba` |
| `openpyxl` | Excel-Export | `pip install openpyxl` |
| `pyreadstat` | SPSS-Dateien laden | `pip install pyreadstat` |

---

## Lizenz

Dieses Projekt ist unter der [MIT-Lizenz](LICENSE) lizenziert.

---

<div align="center">

*cheat

stat Version 4.1 | Autor: Jürgen Leibold | März 2026*

[⬆️ Zurück nach oben](#cheatstat) | [🇬🇧 English Documentation](README_en.md)

</div>

