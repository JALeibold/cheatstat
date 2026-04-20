# cheatstat: Einfache statistische Funktionen für Sozialwissenschaftler

**Eine umfassende Dokumentation für Studierende und Forschende**

[![PyPI](https://img.shields.io/pypi/v/cheatstat?logo=pypi)](https://pypi.org/project/cheatstat/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)

---

## ⚠️ WICHTIGER HINWEIS ZUR GEWICHTUNG

> Diese Implementierung ist eine **Approximation**. Für wissenschaftliche Publikationen
> muss das vollständige Survey-Design (PSU, Strata) berücksichtigt werden.

cheatstat bietet eine vereinfachte Gewichtung, die für **explorative Analysen und
Lehrzwecke** geeignet ist. Es berücksichtigt jedoch **nicht** das vollständige
Survey-Design (Primary Sampling Units, Strata), das für korrekte Standardfehler und
Konfidenzintervalle in komplexen Survey-Daten wie dem ALLBUS erforderlich ist.

**Für wissenschaftliche Publikationen verwenden Sie bitte:**
- R-Pakete wie `survey` oder `srvyr`
- SAS-Prozeduren wie `SURVEYMEANS` oder `SURVEYREG`
- SPSS-Module wie *Complex Samples*

| cheatstat ist **nicht** für | cheatstat ist **ideal** für |
|------------------------------|------------------------------|
| Offizielle statistische Berichte | Lehrveranstaltungen in den Sozialwissenschaften |
| Wissenschaftliche Publikationen | Explorative Datenanalyse |
| Politische Entscheidungsgrundlagen | Schnelle Überprüfung von Hypothesen |
| | Einstieg in statistische Methoden |

---

## Inhaltsverzeichnis

1. [Einleitung](#1-einleitung)
2. [Installation und erste Schritte](#2-installation-und-erste-schritte)
3. [Daten vorbereiten](#3-daten-vorbereiten)
   - [Fehlende Werte analysieren](#31-fehlende-werte-analysieren-missing_report)
   - [Variablen umkodieren](#32-variablen-umkodieren-recode)
4. [Deskriptive Statistik](#4-deskriptive-statistik)
   - [Häufigkeitstabellen](#41-häufigkeitstabellen-fre-und-fre_wl)
   - [Univariate Analyse](#42-univariate-analyse-univ)
5. [Bivariate Analyse](#5-bivariate-analyse)
   - [Kreuztabellen](#51-kreuztabellen-cross_tab)
   - [Zusammenhangsmaße](#52-zusammenhangsmaße-biv)
   - [T-Test](#53-t-test-ttest_u)
6. [Multivariate Analyse](#6-multivariate-analyse)
   - [Regression](#61-regression-regress)
   - [Standardisierte Koeffizienten](#62-standardisierte-koeffizienten-beta)
   - [Reliabilitätsanalyse](#63-reliabilitätsanalyse-cronbach)
7. [Effektstärken und Diagnostik](#7-effektstärken-und-diagnostik)
   - [Effektstärken](#71-effektstärken-effect_size)
   - [Normalverteilungstests](#72-normalverteilungstests-normality_test)
   - [Gruppenvergleich](#73-deskriptiver-gruppenvergleich-compare_groups)
8. [Ergebnisse exportieren](#8-ergebnisse-exportieren-export_results)
9. [Dummy-Variablen](#9-dummy-variablen-create_dummies)
10. [Typische Workflows](#10-typische-workflows)
11. [Kurzanleitung](#11-kurzanleitung)
12. [Anhang](#12-anhang)

---

## 1. Einleitung

**cheatstat** ist ein Python-Paket, das speziell für Studierende und Forschende in den
Sozialwissenschaften entwickelt wurde. Es vereinfacht die Durchführung grundlegender
statistischer Analysen mit Survey-Daten wie dem ALLBUS, GESIS-Sozialerhebungen oder
anderen repräsentativen Bevölkerungsumfragen.

### Warum cheatstat?

Sozialwissenschaftler:innen stehen oft vor folgenden Herausforderungen:

- **Komplexe Survey-Gewichtung**: Viele Pakete ignorieren Survey-Gewichtung
  oder implementieren sie unvollständig
- **Umkodieren von Variablen**: In Python oft umständlich, besonders bei
  komplexen Bedingungen
- **Interpretation von Ergebnissen**: Statistische Ausgaben sind oft zu
  technisch für Einsteiger
- **Berichterstattung**: Ergebnisse müssen in einer für sozialwissenschaftliche
  Publikationen geeigneten Form vorliegen

### Übersicht aller Funktionen

| Funktion | Beschreibung |
|----------|-------------|
| `missing_report(df)` | Fehlende-Werte-Analyse |
| `recode(df, col, mapping)` | Variablen umkodieren |
| `fre(df, col)` | Häufigkeitstabelle |
| `fre_wl(df, col, labels)` | Häufigkeitstabelle mit Labels |
| `uniV(df, col)` | Univariate Analyse (Häufigkeiten + Statistiken) |
| `cross_tab(df, col1, col2)` | Kreuztabelle |
| `biV(df, col1, col2, scale)` | Bivariate Analyse mit Zusammenhangsmaßen |
| `ttest_u(group, g1, g2, dependent, data)` | Unabhängiger t-Test |
| `regress(formula, data)` | OLS-Regression mit Beta-Koeffizienten |
| `beta(formula, data)` | Standardisierte Regressionskoeffizienten |
| `cronbach(df, items)` | Reliabilitätsanalyse (Cronbach's Alpha) |
| `effect_size(type, ...)` | Effektstärken-Rechner |
| `normality_test(df, col)` | Normalverteilungstests |
| `compare_groups(df, group, vars)` | Deskriptiver Gruppenvergleich |
| `export_results(result, file)` | Ergebnisse exportieren |
| `create_dummies(df, col)` | Dummy-Variablen erstellen |
| `help_cheatstat()` | Kurzanleitung |

---

## 2. Installation und erste Schritte

### Installation

```bash
pip install cheatstat
```

Für die vollständige Funktionalität (insbesondere Regression) wird empfohlen,
zusätzlich statsmodels zu installieren:

```bash
pip install statsmodels
```

### Import

Nach der Installation können Sie cheatstat wie folgt importieren:

```python
import cheatstat as cs
```

> Dies ist die empfohlene Importmethode. Alle Funktionen sind dann unter dem
> Präfix `cs.` verfügbar.

### ALLBUS-Beispieldaten laden

Für die folgenden Beispiele verwenden wir den ALLBUS 2018/2019. Die Daten können
von der [GESIS-Website](https://www.gesis.org/allbus) heruntergeladen werden.

```python
import pandas as pd
import pyreadstat

# Rohdaten laden (numerische Werte)
A18N = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "isco08", "eastwest", "iscd11",
             "lm02", "age", "scage", "educ", "pv19",
             "pr04", "pr05", "pr07", "wghtpew"],
    convert_categoricals=False
)

# Daten mit Wertelabels laden
A18L = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "isco08", "eastwest", "iscd11",
             "lm02", "age", "scage", "educ", "pv19",
             "pr04", "pr05", "pr07", "wghtpew"],
    convert_categoricals=True
)
```

> **Hinweis**: `A18N` enthält numerische Werte (z.B. `1.0` für männlich),
> während `A18L` Wertelabels enthält (z.B. `"MALE"`). Beide DataFrames werden
> für `fre_wl()` und `recode()` benötigt.

---

## 3. Daten vorbereiten

### 3.1 Fehlende Werte analysieren: `missing_report()`

Bevor Sie mit der Analyse beginnen, sollten Sie immer einen Überblick über
fehlende Werte gewinnen.

```python
cs.missing_report(A18N).summary()
```

**Ausgabe:**
```
============================================================
  Fehlende-Werte-Bericht
============================================================
  Variablen gesamt: 14
  Zeilen gesamt: 3477
  Vollständige Variablen: 3
  Mit Fehlenden: 11
  Über 5.0% fehlend: 8
  Schwellenwert: 5.0%
------------------------------------------------------------
Variable  n (gültig)  n (fehlend)  % fehlend Status
   scage        1916         1561      44.90      🔴
  isco08        1950         1527      43.92      🔴
     inc        3092          385      11.07      🔴
    pr04        3176          301       8.66      🟡
    pr05        3241          236       6.79      🟡
    pr07        3272          205       5.90      🟡
    lm02        3284          193       5.55      🟡
    pv19        3293          184       5.29      🟡
  iscd11        3454           23       0.66      🟢
     age        3472            5       0.14      🟢
    educ        3474            3       0.09      🟢
eastwest        3477            0       0.00      ✅
     sex        3477            0       0.00      ✅
 wghtpew        3477            0       0.00      ✅
============================================================
```

**Interpretation:**
- `scage` (Alter des Ehepartners) hat 44.90% fehlende Werte – die Variable
  betrifft nur Verheiratete
- `inc` (Einkommen) hat 11.07% fehlende Werte – sollte kritisch geprüft
  werden
- `eastwest`, `sex` und `wghtpew` sind vollständig vorhanden

**Statusampel:**

| Symbol | Bedeutung |
|--------|-----------|
| ✅ | Keine fehlenden Werte |
| 🟢 | Unter Schwellenwert (< 5%) |
| 🟡 | Über Schwellenwert (5–10%) |
| 🔴 | Kritisch (> 10%) |

**Parameter:**

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `threshold` | float | 5.0 | Warnschwelle in Prozent |

---

### 3.2 Variablen umkodieren: `recode()`

Die `recode()`-Funktion unterstützt vielfältige Bedingungsformate:

| Format | Beispiel | Bedeutung |
|--------|---------|-----------|
| Komma-Werte | `'1,2,4'` | Exakt diese Werte |
| Bereich | `'1-6'` | Alle Werte von 1 bis 6 |
| Größer als | `'>5'` | Werte größer 5 |
| Kleiner gleich | `'<=3'` | Werte kleiner oder gleich 3 |
| AND | `'>=2 and <=6'` | Werte zwischen 2 und 6 |
| OR | `'<2 or >8'` | Werte unter 2 oder über 8 |
| NOT | `'not 5'` | Alle Werte außer 5 |
| ELSE | `'else'` | Alle verbleibenden Werte |
| Tupel | `(1, 6)` | Bereich 1 bis 6 |
| Einzelzahl | `5` | Exakt der Wert 5 |

**Parameter:**

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `column` | str | – | Name der Quellspalte |
| `mapping` | dict | – | Zuordnungstabelle |
| `new_name` | str | None | Name der Zielspalte (None = überschreiben) |
| `else_value` | any | NaN | Wert für nicht zugeordnete Fälle |

**Beispiel 1: Bildungskategorien zusammenfassen**

```python
# Originalkodierung:
# 1 = NO CERTIFICATE  2 = LOWEST LEVEL     3 = INTERMEDIARY LEVEL
# 4 = QUALI.UNIV.APPL.SCI.  5 = QUALI.FOR UNIVERSITY
# 6 = OTHER SCHOOL CERTIF.  7 = STILL AT SCHOOL

A18N = cs.recode(A18N, 'educ', {
    '1,2': 1,   # niedrig
    '3,4': 2,   # mittel
    '5':   3    # hoch
}, new_name='educ3')
# ✅ recode: educ → educ3 (3471 zugeordnet, 3 nicht zugeordnet, 6 NaN)
```

**Beispiel 2: Alterskategorien erstellen**

```python
A18N = cs.recode(A18N, 'age', {
    '18-29': 1,   # jung
    '30-49': 2,   # mittel
    '50-99': 3    # alt
}, new_name='age_kat')
```

**Beispiel 3: Komplexe Bedingungen**

```python
# Einkommensdrittel
A18N = cs.recode(A18N, 'inc', {
    '<1000':           1,   # unteres Drittel
    '>=1000 and <2000': 2,  # mittleres Drittel
    '>=2000':          3    # oberes Drittel
}, new_name='inc_kat')
```

**Beispiel 4: Likert-Skala invertieren**

```python
# pv19: 1 = VERY UNLIKELY ... 10 = VERY LIKELY
# Invertierung, damit höhere Werte = höhere CDU/CSU-Ablehnung
A18N = cs.recode(A18N, 'pv19', {
    1: 10, 2: 9, 3: 8, 4: 7, 5: 6,
    6: 5,  7: 4, 8: 3, 9: 2, 10: 1
}, new_name='pv19_r')
```

> **Praxistipp:** Verwenden Sie immer `new_name`, um die Originalvariable
> zu erhalten. Dokumentieren Sie jede Umcodierung in Ihrem Analyseprotokoll.

---

## 4. Deskriptive Statistik

### 4.1 Häufigkeitstabellen: `fre()` und `fre_wl()`

#### `fre()` – Einfache Häufigkeitstabelle

```python
cs.fre(A18N, 'sex', sort=True, round_digits=2)
```

**Ausgabe:**
```
  Ausprägung  Häufigkeiten Prozent kum. Prozente gültigeP kum.gültigeP
0        1.0          1773   50.99         50.99    50.99        50.99
1        2.0          1704   49.01         100.0    49.01        100.0
2      Summe          3477     ---           ---      ---          ---
3     n-nan=          3477     ---           ---      ---          ---
```

**Spalten der Ausgabe:**

| Spalte | Bedeutung |
|--------|-----------|
| `Ausprägung` | Wert der Variable |
| `Häufigkeiten` | Absolute Häufigkeit |
| `Prozent` | Anteil an allen Fällen (inkl. fehlende) |
| `kum. Prozente` | Kumulierter Prozentanteil |
| `gültigeP` | Anteil nur an gültigen Fällen |
| `kum.gültigeP` | Kumulierter gültiger Prozentanteil |

**Parameter:**

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `column` | str | – | Name der Spalte |
| `weight` | str/pd.Series | None | Gewichtung |
| `sort` | bool | True | Nach Wert sortieren |
| `round_digits` | int | 2 | Dezimalstellen |

#### `fre_wl()` – Häufigkeitstabelle mit Wertelabels

Benötigt zwei DataFrames: numerische Werte (`A18N`) und Labels (`A18L`).

```python
cs.fre_wl(A18N, 'educ', A18L, sort_by_value=True, round_digits=2)
```

**Ausgabe:**
```
  Ausprägung                 Label  Häufigkeiten Prozent  gültigeP kum.gültigeP
0        1.0        NO CERTIFICATE            50    1.44      1.44        98.71
1        2.0          LOWEST LEVEL           809   23.30     23.30        88.58
2        3.0    INTERMEDIARY LEVEL          1190   34.37     34.37        34.37
3        4.0  QUALI.UNIV.APPL.SCI.           301    8.69      8.69        97.27
4        5.0  QUALI.FOR UNIVERSITY          1070   30.92     30.92        65.29
5        6.0  OTHER SCHOOL CERTIF.            20    0.58      0.58        99.91
6        7.0       STILL AT SCHOOL            22    0.63      0.63        99.34
7        NaN                   ---            11    0.32      0.32       100.00
8      Summe                   ---          3474     ---       ---          ---
9     n-nan=                   ---          3463     ---       ---          ---
```

**Interpretation:**
- Der größte Anteil (34.37%) hat einen `INTERMEDIARY LEVEL` (Realschulabschluss)
- 30.92% haben `QUALI.FOR UNIVERSITY` (Abitur)
- 23.30% haben `LOWEST LEVEL` (Hauptschulabschluss)
- Nur 1.44% haben `NO CERTIFICATE`

---

### 4.2 Univariate Analyse: `uniV()`

Führt eine umfassende Analyse durch: Häufigkeitstabelle + deskriptive Statistiken.

```python
result = cs.uniV(A18N, 'inc', se=False)
result.summary()
```

**Ausgabe:**
```
============================================================
  Univariate Analyse: inc
============================================================
  Variable: inc
  n (gesamt): 3477
  n (gültig): 3092
------------------------------------------------------------
             Statistik         Wert
                 Modus       2000.0
           25%-Quantil      1000.00
  50%-Quantil (Median)      1500.00
           75%-Quantil      2300.00
                   IQR      1300.00
            Mittelwert    1825.8865
95%-KI (untere Grenze)      1779.31
 95%-KI (obere Grenze)      1872.47
               Minimum        25.00
               Maximum     18000.00
               Varianz 1744997.7526
    Standardabweichung    1320.9836
               Schiefe       2.9523
              Kurtosis      19.0089
                Exzess        16.01
============================================================
```

**Interpretation:**
- Median (1.500 €) liegt deutlich unter dem Mittelwert (1.825,89 €) →
  rechtsschiefe Verteilung
- Starke Schiefe (2.95) und hohe Kurtosis (19.01) zeigen: Einkommen ist
  **nicht normalverteilt**
- Das 95%-KI für den Mittelwert: [1.779,31 €; 1.872,47 €]
- Großer IQR (1.300 €) deutet auf hohe Streuung hin

**Mit Standardfehlern:**

```python
cs.uniV(A18N, 'inc', se=True).summary()
```

Ergibt zusätzliche Spalte `SE` für Mittelwert, Varianz, SD, Schiefe und Kurtosis.

**Zugriff auf Tabellen:**

```python
result = cs.uniV(A18N, 'inc')
result['fre']    # Häufigkeitstabelle als DataFrame
result['stats']  # Deskriptive Statistiken als DataFrame
result.keys()    # Alle verfügbaren Schlüssel
```

**Parameter:**

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `column_name` | str | – | Spaltenname |
| `weight` | str/pd.Series | None | Gewichtung |
| `se` | bool | False | Standardfehler ausgeben |

**Beispiel: Politische Einstellung (pv19)**

```python
cs.uniV(A18N, 'pv19').summary()
```

```
============================================================
  Univariate Analyse: pv19
============================================================
  Variable: pv19
  n (gesamt): 3477
  n (gültig): 3293
------------------------------------------------------------
             Statistik    Wert
                 Modus     1.0
           25%-Quantil    2.00
  50%-Quantil (Median)    6.00
           75%-Quantil    9.00
                   IQR    7.00
            Mittelwert  5.5991
95%-KI (untere Grenze)    5.49
 95%-KI (obere Grenze)    5.71
               Minimum    1.00
               Maximum   10.00
============================================================
```

**Interpretation:**
- Median = 6.0, Mittelwert = 5.60 → annähernd symmetrische Verteilung
- Bimodale Tendenz: Modus bei 1.0 (VERY UNLIKELY), viele Befragte lehnen
  CDU/CSU also stark ab oder befürworten sie stark

---

## 5. Bivariate Analyse

### 5.1 Kreuztabellen: `cross_tab()`

```python
ct = cs.cross_tab(A18N, 'sex', 'eastwest')
ct.summary(show_tables=True)
```

**Ausgabe:**
```
============================================================
  Kreuztabelle: sex × eastwest
============================================================
  Zeilen: sex
  Spalten: eastwest
  n: 3477
------------------------------------------------------------
--- observed ---
eastwest   1.0   2.0  Gesamt
sex
1.0       1223   550    1773
2.0       1164   540    1704
Gesamt    2387  1090    3477

--- col_percent ---
eastwest     1.0     2.0  Gesamt
sex
1.0        51.24   50.46   50.99
2.0        48.76   49.54   49.01
Gesamt    100.00  100.00  100.00

--- row_percent ---
eastwest    1.0    2.0  Gesamt
sex
1.0       68.98  31.02   100.0
2.0       68.31  31.69   100.0
Gesamt    68.65  31.35   100.0

--- expected ---
eastwest      1.0     2.0
sex
1.0       1217.18  555.82
2.0       1169.82  534.18

--- st_residuals ---
eastwest   1.0   2.0
sex
1.0       0.17 -0.25
2.0      -0.17  0.25
============================================================
```

**Interpretation:**
- In West (1.0) und Ost (2.0) ist die Geschlechterverteilung nahezu identisch
  (51.24% vs. 50.46% männlich)
- Standardisierte Residuen < |2.0| → kein signifikanter Zusammenhang

**Zurückgegebene Tabellen:**

| Schlüssel | Inhalt |
|-----------|--------|
| `observed` | Beobachtete Häufigkeiten |
| `col_percent` | Spaltenprozentuierung |
| `row_percent` | Zeilenprozentuierung |
| `total_percent` | Gesamtprozentuierung |
| `expected` | Erwartete Häufigkeiten |
| `residuals` | Einfache Residuen |
| `st_residuals` | Standardisierte Residuen |
| `deff` | Design-Effekt (nur bei Gewichtung) |
| `p_value_deff` | Korrigierter p-Wert (nur bei Gewichtung) |

```python
ct['observed']      # Beobachtete Häufigkeiten als DataFrame
ct['col_percent']   # Spaltenprozentuierung als DataFrame
ct.keys()           # Alle verfügbaren Schlüssel
```

---

### 5.2 Zusammenhangsmaße: `biV()`

```python
# Nominalskaliert: Chi², G², Phi / Cramér's V
cs.biV(A18N, "eastwest", "sex", scale="nominal").summary()
```

**Ausgabe:**
```
============================================================
  Bivariate Analyse: eastwest × sex (nominal)
============================================================
  Variablen: eastwest × sex
  Skalenniveau: nominal
  n: 3477
  Gewichtung: keine
------------------------------------------------------------
    Maß   Wert  p-Wert Sig.
   Chi² 0.1511 0.69750 n.s.
     G² 0.1808 0.67066 n.s.
Phi (φ) 0.0066     ---     
============================================================
```

**Interpretation:**
- Chi² und G² sind nicht signifikant (p > 0.05)
- Phi (φ) = 0.0066 → kein Zusammenhang
- Geschlecht und Wohnort (Ost/West) sind statistisch unabhängig

```python
# Ordinal-metrisch: Pearson-r, Spearman, Kendall, Somers' D
cs.biV(A18N, "eastwest", "pv19", scale="ordinal").summary()
```

**Ausgabe:**
```
============================================================
  Bivariate Analyse: eastwest × pv19 (ordinal-metrisch)
============================================================
  Variablen: eastwest × pv19
  Skalenniveau: ordinal-metrisch
  n: 3293
  Gewichtung: keine
------------------------------------------------------------
            Maß    Wert   p-Wert Sig.
      Pearson-r -0.1000 9.01e-09  ***
   Spearman-Rho -0.1015 5.36e-09  ***
Kendall's Tau-b -0.0876 5.82e-09  ***
Somers' D (Y|X) -0.0571 0.00e+00  ***
Somers' D (X|Y) -0.1075 0.00e+00  ***
============================================================
```

**Interpretation:**
- Alle Maße sind negativ und hoch signifikant (p < 0.001)
- Ostdeutsche (eastwest=1) neigen zu niedrigeren pv19-Werten (geringere
  CDU/CSU-Wahlwahrscheinlichkeit)
- Zusammenhang ist schwach (r = –0.10)

**Parameter:**

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `col1`, `col2` | str | – | Spaltennamen |
| `scale` | str | – | `'nominal'`/`'n'` oder `'ordinal'`/`'om'` |
| `weight` | str/pd.Series | None | Gewichtung |
| `notable` | bool | False | Nur Statistiken, keine Kreuztabelle |

**Skalierungsaliase:**

| Erlaubte Werte | Intern |
|----------------|--------|
| `'nominal'`, `'n'`, `'kategorial'`, `'kat'` | Nominal |
| `'ordinal'`, `'om'`, `'metrisch'`, `'ordinal-metrisch'` | Ordinal-metrisch |

---

### 5.3 T-Test: `ttest_u()`

```python
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N).summary()
```

**Ausgabe:**
```
============================================================
  T-Test: inc nach sex (1.0 vs. 2.0)
============================================================
  Test: Welch-t-Test (keine Varianzhomogenität)
  Gruppen: 1.0 vs. 2.0
  AV: inc
  Gewichtung: keine
------------------------------------------------------------
         Statistik                                    Wert Entscheidung
              Test Welch-t-Test (keine Varianzhomogenität)          ---
       t-Statistik                               18.274488          ---
            p-Wert                                0.00e+00          ***
                df                               2639.2449          ---
     Mittelwert G1                             2212.972739          ---
     Mittelwert G2                             1403.182003          ---
 Differenz (G1-G2)                              809.790736          ---
      95%-KI unten                              722.899717          ---
       95%-KI oben                              896.681754          ---
        Varianz G1                          2308618.966398          ---
        Varianz G2                           788126.643224          ---
         Cohen's d                                  0.6439          ---
        n G1 (roh)                                    1614          ---
        n G2 (roh)                                    1478          ---
        n G1 (eff)                                 1614.00          ---
        n G2 (eff)                                 1478.00          ---
          Levene p                                6.84e-25 Welch-t-Test
          Gruppe 1                                     1.0          ---
          Gruppe 2                                     2.0          ---
Abhängige Variable                                     inc          ---
============================================================
```

**Interpretation:**
- Männer (G1=1.0) verdienen im Durchschnitt **809.79 € mehr** als Frauen (G2=2.0)
- Unterschied ist hoch signifikant (p < 0.001)
- Effektgröße: Cohen's d = 0.64 → **mittlerer bis großer Effekt**
- 95%-KI der Differenz: [722.90 €; 896.68 €]
- Levene-Test: p < 0.001 → Varianzen ungleich → Welch-t-Test korrekt

**Mit Survey-Gewichtung:**

```python
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N, weight='wghtpew').summary()
```

**Ausgabe (Auszug):**
```
     Mittelwert G1    2308.936567
     Mittelwert G2    1417.005032
 Differenz (G1-G2)     891.931534
         Cohen's d         0.6928
        n G1 (eff)        1474.97
        n G2 (eff)        1344.35
```

**Interpretation des Vergleichs (ungewichtet vs. gewichtet):**

| | Ungewichtet | Gewichtet |
|-|------------|----------|
| Differenz | 809.79 € | 891.93 € |
| Cohen's d | 0.64 | 0.69 |
| n (eff) G1 | 1614 | 1474.97 |

Die Gewichtung erhöht die Mittelwertdifferenz, da westdeutsche Männer
(mit höherem Einkommen) durch die Gewichtung stärker gewichtet werden.

**Parameter:**

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `group` | str | – | Name der Gruppenvariable |
| `g1`, `g2` | any | – | Ausprägungen der Gruppen |
| `dependent` | str | – | Abhängige Variable |
| `data` | pd.DataFrame | – | Eingabedaten |
| `weight` | str/pd.Series | None | Gewichtung |
| `levene_test` | str | `'median'` | Art des Levene-Tests |
| `autoLevene` | bool | True | Automatische Test-Entscheidung |

---

## 6. Multivariate Analyse

### 6.1 Regression: `regress()`

```python
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N).summary()
```

**Ausgabe:**
```
============================================================
  Regression: inc ~ sex + eastwest + iscd11
============================================================
  Formel: inc ~ sex + eastwest + iscd11
  Methode: OLS
  n (verwendet): 3083
  n (original): 3477
  n (entfernt): 394
  R²: 0.2649
  R² (adj.): 0.2642
  F: 369.9325
  F p-Wert: 3.62e-205
  F Sig.: ***
  AIC: 52115.9400
  BIC: 52140.0700
  Durbin-Watson: 1.9837
------------------------------------------------------------
 Variable         b       SE Beta (β)        t    p-Wert Sig. 95%-KI unten 95%-KI oben  VIF
Intercept 2172.6065 101.1115      ---  21.4872  1.52e-95  ***    1974.3536   2370.8594  ---
      sex -720.7678  40.9960  -0.2726 -17.5814  5.18e-66  ***    -801.1500   -640.3856 1.01
 eastwest -395.8707  43.7094  -0.1400  -9.0569  2.33e-19  ***    -481.5732   -310.1682 1.00
   iscd11  288.1453  11.4617   0.3898  25.1399 5.18e-127  ***     265.6720    310.6187 1.01
============================================================
```

**Interpretation:**
- `sex` (b = –720.77, β = –0.27): Männer (1) verdienen im Durchschnitt
  **720.77 € mehr** als Frauen (2), kontrolliert für Wohnort und Bildung
- `eastwest` (b = –395.87, β = –0.14): Westdeutsche (1) verdienen **395.87 €
  mehr** als Ostdeutsche (2)
- `iscd11` (b = 288.15, β = 0.39): Stärkster Effekt – pro ISCED-Stufe steigt
  das Einkommen um **288.15 €**
- R² = 0.2649: Das Modell erklärt **26.49%** der Einkommensvarianz
- VIF < 2 für alle Prädiktoren → **keine Multikollinearität**

**Mit Gewichtung und robusten Standardfehlern:**

```python
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N,
           weight='wghtpew', robust=True).summary()
```

**Ausgabe (Auszug):**
```
  Methode: WLS (Gewichtung: wghtpew)
  R²: 0.2683
      sex -791.9079  42.2564  -0.2902 -18.7405  2.71e-74  ***
 eastwest -394.3697  55.1926  -0.1102  -7.1453  1.12e-12  ***
   iscd11  293.8423  11.7433   0.3874  25.0222 6.04e-126  ***
```

**Mit kategorialer Variable:**

```python
cs.regress('inc ~ sex + eastwest + C(iscd11)', data=A18N).summary()
```

**Ausgabe (Auszug):**
```
  R²: 0.2859
C(iscd11)[T.2.0]  415.4761  ...  n.s.   VIF  8.24 ⚠️
C(iscd11)[T.3.0]  721.0482  ...   **   VIF 29.88 ⚠️
C(iscd11)[T.7.0] 1813.1817  ...  ***   VIF 20.13 ⚠️
C(iscd11)[T.8.0] 3127.2537  ...  ***   VIF  3.54
```

> **Praxistipp:** Hohe VIF-Werte (> 5: ⚠️, > 10: 🔴) deuten auf
> Multikollinearität hin. Bei kategorialen Variablen ist dies häufig, da die
> Dummy-Variablen miteinander korrelieren.

**Zugriff auf das statsmodels-Objekt:**

```python
result = cs.regress('inc ~ sex + eastwest + iscd11', data=A18N)
result['model'].summary()     # Original statsmodels-Ausgabe
result['model'].resid          # Residuen
result['model'].fittedvalues   # Vorhergesagte Werte
result['anova']                # ANOVA-Tabelle
```

**Parameter:**

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `formula` | str | – | R-Formel: `'y ~ x1 + x2 + ...'` |
| `data` | pd.DataFrame | – | Eingabedaten |
| `weight` | str | None | Gewichtungsspalte (WLS) |
| `robust` | bool | False | Robuste SE (HC3) |
| `show_beta` | bool | True | Standardisierte β anzeigen |
| `show_ci` | bool | True | 95%-KI anzeigen |
| `show_vif` | bool | True | VIF anzeigen |

---

### 6.2 Standardisierte Koeffizienten: `beta()`

```python
# Schnelle Variante: nur β-Koeffizienten
cs.beta('inc ~ sex + eastwest + iscd11', data=A18N, full=True).summary()
```

**Ausgabe:**
```
============================================================
  Standardisierte Regression: inc ~ sex + eastwest + iscd11
============================================================
  R²: 0.2649    R² (adj.): 0.2642
  F: 369.9325   F p: 1.11e-16  ***
------------------------------------------------------------
Variable Beta (β) SE (β)        t   p-Wert Sig.  r(y,x)
     sex  -0.2726 0.0155 -17.5814 0.00e+00  *** -0.3078
eastwest  -0.1400 0.0155  -9.0569 0.00e+00  *** -0.1451
  iscd11   0.3898 0.0155  25.1399 0.00e+00  ***  0.4123
============================================================
```

**Interpretation:**
- `iscd11` hat den stärksten standardisierten Effekt (β = 0.39)
- `r(y,x)` = bivariate Korrelation ohne Kontrolle anderer Variablen
- Differenz zwischen β und r zeigt den Einfluss der Kontrollvariablen

---

### 6.3 Reliabilitätsanalyse: `cronbach()`

```python
cs.cronbach(A18N, ['pr04', 'pr05', 'pr07']).summary()
```

**Ausgabe:**
```
============================================================
  Reliabilitätsanalyse (3 Items)
============================================================
  Cronbach's Alpha: -0.2415
  Bewertung: inakzeptabel
  Items: 3
  n (Listwise): 3055
  n (entfernt): 422
------------------------------------------------------------
Item    M   SD   r(it) Alpha ohne   Empfehlung
pr04 2.20 0.89 -0.1053    -0.1369 ⚠️ entfernen
pr05 1.95 0.83 -0.0987    -0.1591 ⚠️ entfernen
pr07 3.20 0.78 -0.1017    -0.1501 ⚠️ entfernen
============================================================
```

**Interpretation:**
- Cronbach's Alpha = –0.24: **Inakzeptabel** – die Items messen keine gemeinsame
  Dimension
- Alle Item-Total-Korrelationen sind negativ – mögliche Ursache: pr04/pr05 fragen
  nach Vorteilen (zustimmen = positiv), pr07 fragt nach Fremdheit (zustimmen =
  negativ) → Skalenrichtung prüfen!

**Alpha-Bewertung:**

| Alpha | Bewertung |
|-------|-----------|
| ≥ 0.90 | Exzellent |
| ≥ 0.80 | Gut |
| ≥ 0.70 | Akzeptabel |
| ≥ 0.60 | Fragwürdig |
| ≥ 0.50 | Schlecht |
| < 0.50 | Inakzeptabel |

---

## 7. Effektstärken und Diagnostik

### 7.1 Effektstärken: `effect_size()`

```python
cs.effect_size('cohen_d', m1=2213, m2=1403, sd1=1519, sd2=888).summary()
```

**Ausgabe:**
```
============================================================
  Effektstärke: cohen_d
============================================================
  m1: 2213
  m2: 1403
  sd1: 1519
  sd2: 888
------------------------------------------------------------
      Maß   Wert Bewertung
Cohen's d 0.6439    mittel
r (aus d) 0.3066       ---
============================================================
```

**Verfügbare Typen:**

| Typ | Benötigte Parameter | Beschreibung |
|-----|--------------------|----|
| `'cohen_d'` | `m1, m2, sd1, sd2` (opt: `n1, n2`) | Cohen's d |
| `'eta_sq'` | `f, df1, df2` | Eta² |
| `'omega_sq'` | `f, df1, df2` (opt: `n`) | Omega² |
| `'r_to_d'` | `r` | Korrelation → Cohen's d |
| `'d_to_r'` | `d` | Cohen's d → Korrelation |
| `'odds_ratio'` | `a, b, c, d` | Odds Ratio aus 2×2-Tabelle |

```python
cs.effect_size('r_to_d', r=0.12).summary()
# → r → d: 0.2417  (r = 0.1200)

cs.effect_size('odds_ratio', a=30, b=10, c=20, d=40).summary()
# → Odds Ratio: 6.00, 95%-KI: [2.25, 16.00]
```

---

### 7.2 Normalverteilungstests: `normality_test()`

```python
cs.normality_test(A18N, 'inc').summary()
```

**Ausgabe:**
```
============================================================
  Normalverteilungstests: inc
============================================================
  Variable: inc
  n: 3092
  M: 1825.8865
  SD: 1320.9836
------------------------------------------------------------
               Test Statistik   p-Wert Sig.             Ergebnis
       Shapiro-Wilk    0.7987 3.04e-52  *** NICHT normalverteilt
 Kolmogorov-Smirnov    0.1387 2.34e-52  *** NICHT normalverteilt
  Schiefe (z=67.02)    2.9523      ---   ⚠️               schief
Kurtosis (z=215.76)   19.0089      ---   ⚠️   nicht mesokurtisch
============================================================
```

**Interpretation:**
- Beide Tests signifikant (p < 0.001) → klare Abweichung von der Normalverteilung
- Für das Einkommen ist eine rechtsschiefe Verteilung typisch
- Bei n > 500 sind Normalverteilungstests sehr sensitiv – grafische Prüfung
  zusätzlich empfohlen

---

### 7.3 Deskriptiver Gruppenvergleich: `compare_groups()`

```python
cs.compare_groups(A18N, 'sex', ['inc', 'age', 'educ']).summary()
```

**Ausgabe:**
```
============================================================
  Gruppenvergleich nach sex
============================================================
  Gruppen: [1.0, 2.0]
  Variablen: ['inc', 'age', 'educ']
------------------------------------------------------------
Variable M (1.0) SD (1.0)  n (1.0) M (2.0) SD (2.0)  n (2.0)
     inc 2212.97  1519.41     1614 1403.18   887.76     1478
     age   51.42    17.91     1772   51.95    17.36     1700
    educ    3.49     1.26     1771    3.48     1.22     1703
============================================================
```

**Interpretation:**
- Deutlicher Einkommensunterschied: Männer +809 €
- Alter und Bildung sind fast identisch zwischen den Gruppen

---

## 8. Ergebnisse exportieren: `export_results()`

```python
result = cs.regress('inc ~ sex + eastwest + iscd11', data=A18N)
cs.export_results(result, 'regression_ergebnis', format='excel')
# ✅ Exportiert: regression_ergebnis.xlsx (3 Sheets)
```

**Unterstützte Formate:**

| Format | Dateiendung | Anwendung |
|--------|------------|-----------|
| `'excel'` | `.xlsx` | Microsoft Excel, LibreOffice Calc |
| `'csv'` | `.csv` | Tabellenverarbeitung, R, SPSS |
| `'html'` | `.html` | Web-Präsentation, Berichte |
| `'latex'` | `.tex` | Wissenschaftliche Publikationen |

```python
cs.export_results(result, 'ergebnis', format='latex')
# ✅ Exportiert: ergebnis.tex
```

---

## 9. Dummy-Variablen: `create_dummies()`

```python
A18N = cs.create_dummies(A18N, 'educ', prefix='educ')
# Erzeugt Spalten: educ_1, educ_2, educ_3, educ_4, educ_5, educ_6, educ_7
```

Dummy-Variablen werden direkt an den DataFrame angehängt. Dezimalstellen werden
entfernt (z.B. `educ_3` statt `educ_3.0`).

---

## 10. Typische Workflows

### Workflow 1: Deskriptive Analyse einer Variablen

```python
# Schritt 1: Fehlende Werte prüfen
cs.missing_report(A18N).summary()

# Schritt 2: Häufigkeitstabelle mit Labels
cs.fre_wl(A18N, 'pv19', A18L, sort_by_value=True)

# Schritt 3: Deskriptive Statistiken
cs.uniV(A18N, 'pv19', se=True).summary()

# Schritt 4: Normalverteilung prüfen
cs.normality_test(A18N, 'pv19').summary()
```

### Workflow 2: Zusammenhangsanalyse

```python
# Schritt 1: Kreuztabelle mit allen Tabellen
cs.cross_tab(A18N, 'eastwest', 'pv19').summary(show_tables=True)

# Schritt 2: Zusammenhangsmaße
cs.biV(A18N, 'eastwest', 'pv19', scale='ordinal').summary()

# Schritt 3: Nur Statistiken (keine Kreuztabelle)
cs.biV(A18N, 'eastwest', 'pv19', scale='ordinal', notable=True).summary()
```

### Workflow 3: Regression

```python
# Schritt 1: Variablen umkodieren
A18N = cs.recode(A18N, 'educ', {'1,2': 1, '3,4': 2, '5': 3}, new_name='educ3')

# Schritt 2: OLS-Regression mit Gewichtung
result = cs.regress('inc ~ sex + eastwest + educ3',
                    data=A18N, weight='wghtpew', robust=True)
result.summary()

# Schritt 3: Exportieren
cs.export_results(result, 'regression_inc', format='excel')
```

### Workflow 4: Reliabilitätsanalyse

```python
# Schritt 1: Items prüfen
for item in ['pr04', 'pr05', 'pr07']:
    cs.uniV(A18N, item).summary()

# Schritt 2: Reliabilitätsanalyse
cs.cronbach(A18N, ['pr04', 'pr05', 'pr07']).summary()
```

---

## 11. Kurzanleitung

```python
cs.help_cheatstat()
```

Gibt eine kompakte Übersicht über alle Funktionen in der Konsole aus.

---

## 12. Anhang

### ALLBUS-Variablenreferenz (Version 2018/2019)

| Variable | Beschreibung | Skalenniveau | Wertebereich |
|----------|-------------|-------------|-------------|
| `sex` | Geschlecht | nominal | 1=Mann, 2=Frau |
| `inc` | Monatliches Nettoeinkommen | metrisch | 25–18.000 € |
| `eastwest` | Wohnort | nominal | 1=West, 2=Ost |
| `iscd11` | Bildung (ISCED 2011) | ordinal | 1–8 |
| `lm02` | Fernsehdauer/Tag (Minuten) | metrisch | 1–1.200 |
| `age` | Alter | metrisch | 18–95 Jahre |
| `scage` | Alter des Ehepartners | metrisch | 21–96 Jahre |
| `educ` | Schulabschluss | ordinal | 1–7 |
| `pv19` | Wahrscheinlichkeit CDU/CSU zu wählen | ordinal | 1–10 |
| `pr04` | Wiedervereinigung: Vorteile für Westen | ordinal | 1–4 |
| `pr05` | Wiedervereinigung: Vorteile für Osten | ordinal | 1–4 |
| `pr07` | Bürger fremd im anderen Teil Deutschlands? | ordinal | 1–4 |
| `wghtpew` | Personengewicht | metrisch | 0.54–1.21 |

### Signifikanzsterne

| Symbol | p-Wert | Interpretation |
|--------|--------|---------------|
| `***` | < 0.001 | Hoch signifikant |
| `**` | < 0.01 | Signifikant |
| `*` | < 0.05 | Tendenziell signifikant |
| `n.s.` | ≥ 0.05 | Nicht signifikant |

### Effektstärken-Bewertung (Cohen, 1988)

| Maß | Klein | Mittel | Groß |
|-----|-------|--------|------|
| Cohen's d | 0.20 | 0.50 | 0.80 |
| r | 0.10 | 0.30 | 0.50 |
| Eta² | 0.01 | 0.06 | 0.14 |
| Phi/Cramér's V | 0.10 | 0.30 | 0.50 |

### Häufige Fehlermeldungen

| Fehlermeldung | Ursache | Lösung |
|--------------|---------|--------|
| `ValueError: Gewichtungsspalte '...' nicht gefunden` | Tippfehler im Spaltennamen | `print(df.columns)` |
| `ValueError: Gruppe '...' existiert nicht` | Falscher Gruppentyp | `print(df['var'].unique())` |
| `LinAlgError: Singular matrix` | Multikollinearität | Redundante Prädiktoren entfernen |
| `cronbach(): Alpha negativ` | Unterschiedliche Skalenrichtungen | Items invertieren mit `recode()` |

---

*cheatstat Version 4.1.2 | Autor: Jürgen Leibold | März 2026*

[🇬🇧 English Documentation](../en/index.md) | [⬆️ Zurück zur Übersicht](../../README.md)