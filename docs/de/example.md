# Beispiele mit ALLBUS 2018/2019-Daten

[← Grundlegende Nutzung](usage.md) | [API-Referenz →](api.md) |
[🇬🇧 English](../en/examples.md)

---

## Inhaltsverzeichnis

1. [Daten laden](#1-daten-laden)
2. [Fehlende Werte analysieren](#2-fehlende-werte-analysieren)
3. [Variablen umkodieren](#3-variablen-umkodieren)
4. [Häufigkeitstabellen](#4-häufigkeitstabellen)
5. [Univariate Analyse](#5-univariate-analyse)
6. [Bivariate Analyse: Kreuztabellen](#6-bivariate-analyse-kreuztabellen)
7. [Bivariate Analyse: Zusammenhangsmaße](#7-bivariate-analyse-zusammenhangsmaße)
8. [T-Test](#8-t-test)
9. [Regression](#9-regression)
10. [Reliabilitätsanalyse](#10-reliabilitätsanalyse)
11. [Effektstärken](#11-effektstärken)
12. [Normalverteilungstests](#12-normalverteilungstests)
13. [Gruppenvergleich](#13-gruppenvergleich)
14. [Export](#14-export)
15. [Vollständiger Analyseablauf](#15-vollständiger-analyseablauf)

---

## 1. Daten laden

```python
import pandas as pd
import numpy as np
import cheatstat as cs

# Numerische Werte (für Analysen)
A18N = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "isco08", "eastwest", "iscd11",
             "lm02", "age", "scage", "educ", "pv19",
             "pr04", "pr05", "pr07", "wghtpew"],
    convert_categoricals=False
)

# Wertelabels (für fre_wl)
A18L = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "isco08", "eastwest", "iscd11",
             "lm02", "age", "scage", "educ", "pv19",
             "pr04", "pr05", "pr07", "wghtpew"],
    convert_categoricals=True
)

print(f"Datensatz geladen: {A18N.shape[0]} Fälle, {A18N.shape[1]} Variablen")
```

---

## 2. Fehlende Werte analysieren

```python
cs.missing_report(A18N).summary()
```

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

**Schlussfolgerungen:**
- `scage` (Alter Ehepartner, 44.90%) und `isco08` (43.92%) nur für
  Teilgruppen vorhanden
- `inc` (11.07% fehlend) sollte kritisch betrachtet werden

---

## 3. Variablen umkodieren

### Bildungskategorien erstellen

```python
# educ: 1=NO CERT, 2=LOWEST, 3=INTERM., 4=UNIV.APPL., 5=UNIVERSITY
# 6=OTHER, 7=STILL AT SCHOOL
A18N = cs.recode(A18N, 'educ', {
    '1,2': 1,   # niedrig: kein/Hauptschulabschluss
    '3,4': 2,   # mittel:  Realschule/Fachhochschulreife
    '5':   3    # hoch:    Abitur
}, new_name='educ3')
# ✅ recode: educ → educ3 (3471 zugeordnet, 3 nicht zugeordnet, 6 NaN)
```

### Alterskategorien erstellen

```python
A18N = cs.recode(A18N, 'age', {
    '18-34': 1,   # Junge Erwachsene
    '35-54': 2,   # Mittleres Alter
    '55-99': 3    # Ältere
}, new_name='age3')
```

### Einkommensgruppen erstellen

```python
A18N = cs.recode(A18N, 'inc', {
    '>0 and <1000':  1,   # Niedrigeinkommen
    '>=1000 and <2500': 2,  # Mitteleinkommen
    '>=2500':        3    # Hoheinkommen
}, new_name='inc3')
```

### Likert-Skala invertieren (pv19)

```python
# pv19: 1=VERY UNLIKELY bis 10=VERY LIKELY (CDU/CSU wählen)
# Invertieren für bessere Interpretation
A18N = cs.recode(A18N, 'pv19', {
    1: 10, 2: 9, 3: 8, 4: 7, 5: 6,
    6: 5,  7: 4, 8: 3, 9: 2, 10: 1
}, new_name='pv19_r')
```

---

## 4. Häufigkeitstabellen

### Geschlecht (fre)

```python
cs.fre(A18N, 'sex', sort=True, round_digits=2)
```

```
  Ausprägung  Häufigkeiten Prozent kum. Prozente gültigeP kum.gültigeP
0        1.0          1773   50.99         50.99    50.99        50.99
1        2.0          1704   49.01         100.0    49.01        100.0
2      Summe          3477     ---           ---      ---          ---
3     n-nan=          3477     ---           ---      ---          ---
```

### Bildungsabschluss mit Labels (fre_wl)

```python
cs.fre_wl(A18N, 'educ', A18L, sort_by_value=True, round_digits=2)
```

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

### CDU/CSU-Wahlwahrscheinlichkeit mit Labels

```python
cs.fre_wl(A18N, 'pv19', A18L['pv19'], sort_by_value=True, round_digits=2)
```

```
   Ausprägung          Label  Häufigkeiten  Prozent  gültigeP kum.gültigeP
0         1.0  VERY UNLIKELY           651    18.72     18.72        18.72
1         2.0             ..           196     5.64      5.64        24.36
2         3.0             ..           258     7.42      7.42        31.78
...
9        10.0    VERY LIKELY           577    16.59     16.59       100.00
10        NaN            ---           184     5.29      5.29          ---
```

---

## 5. Univariate Analyse

### Einkommen (metrische Variable)

```python
cs.uniV(A18N, 'inc').summary()
```

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

### Lebenszufriedenheit (lm02 – Fernsehdauer)

```python
cs.uniV(A18N, 'lm02').summary()
```

```
             Statistik      Wert
                 Modus     120.0
           25%-Quantil      90.00
  50%-Quantil (Median)    120.00
           75%-Quantil    180.00
            Mittelwert  142.9991
    Standardabweichung   92.1817
               Schiefe    2.5866
              Kurtosis   14.3306
```

### Mit Standardfehlern

```python
cs.uniV(A18N, 'inc', se=True).summary()
```

```
      Statistik         Wert   SE
     Mittelwert    1825.8865 22.82
        Varianz 1744997.7526 97.56
 Standardabw.     1320.9836  0.58
       Schiefe       2.9523  0.044
      Kurtosis      19.0089  0.088
```

---

## 6. Bivariate Analyse: Kreuztabellen

### Geschlecht × Wohnort (Ost/West)

```python
ct = cs.cross_tab(A18N, 'sex', 'eastwest')
ct.summary(show_tables=True)
```

```
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
```

**Interpretation:** Standardisierte Residuen < |2| → keine signifikante
Abweichung von der Unabhängigkeit

### Kreuztabelle abrufen

```python
ct['observed']         # pd.DataFrame
ct['col_percent']      # pd.DataFrame
ct['st_residuals']     # pd.DataFrame
```

---

## 7. Bivariate Analyse: Zusammenhangsmaße

### Nominal: Geschlecht × Wohnort

```python
cs.biV(A18N, "eastwest", "sex", scale="nominal").summary()
```

```
============================================================
  Bivariate Analyse: eastwest × sex (nominal)
============================================================
  n: 3477
------------------------------------------------------------
    Maß   Wert  p-Wert Sig.
   Chi² 0.1511 0.69750 n.s.
     G² 0.1808 0.67066 n.s.
Phi (φ) 0.0066     ---     
============================================================
```

**Interpretation:** Kein signifikanter Zusammenhang zwischen Geschlecht
und Wohnort (Ost/West)

### Ordinal: Wohnort × CDU/CSU-Wahlwahrscheinlichkeit

```python
cs.biV(A18N, "eastwest", "pv19", scale="ordinal").summary()
```

```
============================================================
  Bivariate Analyse: eastwest × pv19 (ordinal-metrisch)
============================================================
  n: 3293
------------------------------------------------------------
            Maß    Wert   p-Wert Sig.
      Pearson-r -0.1000 9.01e-09  ***
   Spearman-Rho -0.1015 5.36e-09  ***
Kendall's Tau-b -0.0876 5.82e-09  ***
Somers' D (Y|X) -0.0571 0.00e+00  ***
Somers' D (X|Y) -0.1075 0.00e+00  ***
============================================================
```

**Interpretation:** Signifikanter negativer Zusammenhang –
Westdeutsche (1) haben tendenziell höhere CDU/CSU-Wahlwahrscheinlichkeit
als Ostdeutsche (2)

### Nur Statistiken (ohne Kreuztabelle)

```python
cs.biV(A18N, "eastwest", "sex", scale="nominal",
       notable=True).summary()
```

---

## 8. T-Test

### Einkommensunterschiede nach Geschlecht (ohne Gewichtung)

```python
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N).summary()
```

```
============================================================
  T-Test: inc nach sex (1.0 vs. 2.0)
============================================================
  Test: Welch-t-Test (keine Varianzhomogenität)
  Gewichtung: keine
------------------------------------------------------------
       t-Statistik                               18.274488
            p-Wert                                0.00e+00   ***
                df                               2639.2449
     Mittelwert G1                             2212.972739
     Mittelwert G2                             1403.182003
 Differenz (G1-G2)                              809.790736
      95%-KI unten                              722.899717
       95%-KI oben                              896.681754
         Cohen's d                                  0.6439
          Levene p                                6.84e-25   Welch-t-Test
============================================================
```

### Mit Survey-Gewichtung

```python
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N, weight='wghtpew').summary()
```

```
============================================================
  T-Test: inc nach sex (1.0 vs. 2.0)
============================================================
  Test: Welch-t-Test
  Gewichtung: wghtpew
------------------------------------------------------------
       t-Statistik      18.793315
            p-Wert       0.00e+00   ***
                df      2419.2600
     Mittelwert G1    2308.936567
     Mittelwert G2    1417.005032
 Differenz (G1-G2)     891.931534
      95%-KI unten     798.865001
       95%-KI oben     984.998068
         Cohen's d         0.6928
        n G1 (eff)        1474.97
        n G2 (eff)        1344.35
============================================================
```

**Vergleich ungewichtet vs. gewichtet:**

| | Ungewichtet | Gewichtet |
|-|------------|----------|
| Mittelwert Männer | 2212.97 € | 2308.94 € |
| Mittelwert Frauen | 1403.18 € | 1417.01 € |
| Differenz | 809.79 € | 891.93 € |
| Cohen's d | 0.64 | 0.69 |

---

## 9. Regression

### OLS-Regression: Einkommen nach Geschlecht, Wohnort und Bildung

```python
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N).summary()
```

```
============================================================
  Regression: inc ~ sex + eastwest + iscd11
============================================================
  Methode: OLS
  n (verwendet): 3083   n (entfernt): 394
  R²: 0.2649           R² (adj.): 0.2642
  F: 369.9325          F p-Wert: 3.62e-205  ***
  AIC: 52115.94        BIC: 52140.07
  Durbin-Watson: 1.9837
------------------------------------------------------------
 Variable         b       SE Beta (β)        t    p-Wert Sig. 95%-KI unten 95%-KI oben  VIF
Intercept 2172.6065 101.1115      ---  21.4872  1.52e-95  ***    1974.3536   2370.8594  ---
      sex -720.7678  40.9960  -0.2726 -17.5814  5.18e-66  ***    -801.1500   -640.3856 1.01
 eastwest -395.8707  43.7094  -0.1400  -9.0569  2.33e-19  ***    -481.5732   -310.1682 1.00
   iscd11  288.1453  11.4617   0.3898  25.1399 5.18e-127  ***     265.6720    310.6187 1.01
============================================================
```

### Mit Gewichtung und robusten Standardfehlern

```python
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N,
           weight='wghtpew', robust=True).summary()
```

```
  Methode: WLS (Gewichtung: wghtpew)
  R²: 0.2683   R² (adj.): 0.2676
------------------------------------------------------------
      sex -791.9079  42.2564  -0.2902 -18.7405  2.71e-74  ***
 eastwest -394.3697  55.1926  -0.1102  -7.1453  1.12e-12  ***
   iscd11  293.8423  11.7433   0.3874  25.0222 6.04e-126  ***
```

### Mit kategorialer Bildungsvariable

```python
cs.regress('inc ~ sex + eastwest + C(iscd11)', data=A18N).summary()
```

```
  R²: 0.2859   R² (adj.): 0.2838
------------------------------------------------------------
C(iscd11)[T.2.0]  415.4761  ...  n.s.   VIF  8.24 ⚠️
C(iscd11)[T.3.0]  721.0482  ...   **   VIF 29.88 ⚠️
C(iscd11)[T.7.0] 1813.1817  ...  ***   VIF 20.13 ⚠️
C(iscd11)[T.8.0] 3127.2537  ...  ***   VIF  3.54
             sex -718.2815  ...  ***   VIF  1.02
        eastwest -393.4467  ...  ***   VIF  1.02
```

### Standardisierte Koeffizienten (beta)

```python
cs.beta('inc ~ sex + eastwest + iscd11', data=A18N, full=True).summary()
```

```
  R²: 0.2649    R² (adj.): 0.2642    F: 369.9325  ***
------------------------------------------------------------
Variable Beta (β) SE (β)        t   p-Wert Sig.  r(y,x)
     sex  -0.2726 0.0155 -17.5814 0.00e+00  *** -0.3078
eastwest  -0.1400 0.0155  -9.0569 0.00e+00  *** -0.1451
  iscd11   0.3898 0.0155  25.1399 0.00e+00  ***  0.4123
```

### Zugriff auf statsmodels-Objekt

```python
result = cs.regress('inc ~ sex + eastwest + iscd11', data=A18N)
result['model'].summary()          # Original statsmodels-Ausgabe
result['model'].resid              # Residuen als pd.Series
result['model'].fittedvalues       # Vorhergesagte Werte
result['anova']                    # ANOVA-Tabelle Typ 2
```

---

## 10. Reliabilitätsanalyse

### Cronbach's Alpha für Wiedervereinigungsskala

```python
cs.cronbach(A18N, ['pr04', 'pr05', 'pr07']).summary()
```

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

**Interpretation:** Negatives Alpha zeigt, dass die Items keine
gemeinsame Dimension messen. pr04/pr05 (Wiedervereinigung-Vorteile)
und pr07 (Fremdheitsgefühl) messen unterschiedliche Konzepte.

---

## 11. Effektstärken

### Cohen's d für Einkommensunterschied

```python
# Werte aus dem T-Test verwenden
cs.effect_size('cohen_d',
               m1=2212.97, m2=1403.18,
               sd1=1519.41, sd2=887.76,
               n1=1614, n2=1478).summary()
```

```
      Maß   Wert Bewertung
Cohen's d 0.6439    mittel
r (aus d) 0.3066       ---
```

### Korrelation → Cohen's d Konvertierung

```python
cs.effect_size('r_to_d', r=0.10).summary()
```

```
  Maß   Wert  Bewertung
r → d 0.2010 r = 0.1000
```

### Odds Ratio

```python
cs.effect_size('odds_ratio', a=30, b=10, c=20, d=40).summary()
```

```
      Maß        Wert Bewertung
Odds Ratio        6.00       ---
95%-KI unten      2.25       ---
95%-KI oben      16.00       ---
     ln(OR)       1.79       ---
```

---

## 12. Normalverteilungstests

### Einkommen auf Normalverteilung prüfen

```python
cs.normality_test(A18N, 'inc').summary()
```

```
============================================================
  Normalverteilungstests: inc
============================================================
  n: 3092     M: 1825.8865     SD: 1320.9836
------------------------------------------------------------
               Test Statistik   p-Wert Sig.             Ergebnis
       Shapiro-Wilk    0.7987 3.04e-52  *** NICHT normalverteilt
 Kolmogorov-Smirnov    0.1387 2.34e-52  *** NICHT normalverteilt
  Schiefe (z=67.02)    2.9523      ---   ⚠️               schief
Kurtosis (z=215.76)   19.0089      ---   ⚠️   nicht mesokurtisch
============================================================
```

**Schlussfolgerung:** Einkommen ist stark rechtsschief und nicht
normalverteilt – für parametrische Tests sollte robuste Methodik
(Welch-t-Test, robuste SE in Regression) verwendet werden.

---

## 13. Gruppenvergleich

### Mittelwertvergleich: Männer vs. Frauen

```python
cs.compare_groups(A18N, 'sex', ['inc', 'age', 'educ']).summary()
```

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

### Ost-West-Vergleich

```python
cs.compare_groups(A18N, 'eastwest',
                  ['inc', 'age', 'pv19']).summary()
```

---

## 14. Export

### Excel-Export

```python
result = cs.regress('inc ~ sex + eastwest + iscd11', data=A18N)
cs.export_results(result, 'regression_ergebnis')
# ✅ Exportiert: regression_ergebnis.xlsx (3 Sheets)
```

### LaTeX-Export für Seminararbeiten

```python
cs.export_results(result, 'regression_ergebnis', format='latex')
# ✅ Exportiert: regression_ergebnis.tex
```

### CSV-Export

```python
cs.export_results(result, 'regression_ergebnis', format='csv', decimal=',')
# ✅ Exportiert: regression_ergebnis_Statistiken.csv
```

---

## 15. Vollständiger Analyseablauf

### Forschungsfrage: Was erklärt Einkommensunterschiede?

```python
# === SCHRITT 1: Daten laden ===
import pandas as pd
import cheatstat as cs

A18N = pd.read_spss('ALLBUS2018.sav',
    usecols=["sex", "inc", "eastwest", "iscd11", "educ", "wghtpew"],
    convert_categoricals=False)

# === SCHRITT 2: Datenqualität prüfen ===
cs.missing_report(A18N).summary()

# === SCHRITT 3: Variablen erkunden ===
cs.uniV(A18N, 'inc').summary()
cs.uniV(A18N, 'sex').summary()
cs.uniV(A18N, 'eastwest').summary()

# === SCHRITT 4: Normalverteilung prüfen ===
cs.normality_test(A18N, 'inc').summary()

# === SCHRITT 5: Bivariate Zusammenhänge ===
# Geschlecht × Einkommen (T-Test)
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N).summary()

# Wohnort × Einkommen (T-Test)
cs.ttest_u(group='eastwest', g1=1.0, g2=2.0,
           dependent='inc', data=A18N).summary()

# Bildung × Einkommen (Korrelation)
cs.biV(A18N, 'iscd11', 'inc', scale='ordinal',
       notable=True).summary()

# === SCHRITT 6: Deskriptiver Gruppenvergleich ===
cs.compare_groups(A18N, 'sex', ['inc', 'iscd11']).summary()

# === SCHRITT 7: Multivariate Regression ===
result = cs.regress(
    'inc ~ sex + eastwest + iscd11',
    data=A18N,
    weight='wghtpew',
    robust=True
)
result.summary()

# === SCHRITT 8: Effektstärken berechnen ===
cs.effect_size('cohen_d',
               m1=2309, m2=1417,
               sd1=1519, sd2=888).summary()

# === SCHRITT 9: Ergebnisse exportieren ===
cs.export_results(result, 'einkommensanalyse_final')
```

---

*cheatstat Version 4.1 | Autor: Jürgen Leibold | März 2026*

[→ API-Referenz](api.md) |
[← Grundlegende Nutzung](usage.md) |
[← Zurück zur Übersicht](index.md)