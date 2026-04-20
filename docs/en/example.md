# Examples with ALLBUS 2018/2019 Data

[← Basic Usage](usage.md) | [API Reference →](api.md) |
[🇩🇪 Deutsch](../de/examples.md)

---

## Table of Contents

1. [Loading Data](#1-loading-data)
2. [Missing Value Analysis](#2-missing-value-analysis)
3. [Recoding Variables](#3-recoding-variables)
4. [Frequency Tables](#4-frequency-tables)
5. [Univariate Analysis](#5-univariate-analysis)
6. [Bivariate Analysis: Cross-Tabulations](#6-bivariate-analysis-cross-tabulations)
7. [Bivariate Analysis: Association Measures](#7-bivariate-analysis-association-measures)
8. [T-Test](#8-t-test)
9. [Regression](#9-regression)
10. [Reliability Analysis](#10-reliability-analysis)
11. [Effect Sizes](#11-effect-sizes)
12. [Normality Tests](#12-normality-tests)
13. [Group Comparison](#13-group-comparison)
14. [Export](#14-export)
15. [Complete Analysis Workflow](#15-complete-analysis-workflow)

---

## 1. Loading Data

```python
import pandas as pd
import numpy as np
import cheatstat as sis

# Numeric values (for analyses)
A18N = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "isco08", "eastwest", "iscd11",
             "lm02", "age", "scage", "educ", "pv19",
             "pr04", "pr05", "pr07", "wghtpew"],
    convert_categoricals=False
)

# Value labels (for fre_wl)
A18L = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "isco08", "eastwest", "iscd11",
             "lm02", "age", "scage", "educ", "pv19",
             "pr04", "pr05", "pr07", "wghtpew"],
    convert_categoricals=True
)

print(f"Dataset loaded: {A18N.shape[0]} cases, {A18N.shape[1]} variables")
```

---

## 2. Missing Value Analysis

```python
sis.missing_report(A18N).summary()
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

**Key findings:**
- `scage` (partner's age, 44.90%) and `isco08` (43.92%) are only
  available for subgroups
- `inc` (11.07% missing) requires careful consideration

---

## 3. Recoding Variables

### Creating Education Categories

```python
# educ: 1=NO CERT, 2=LOWEST, 3=INTERM., 4=UNIV.APPL., 5=UNIVERSITY
A18N = sis.recode(A18N, 'educ', {
    '1,2': 1,   # low: no/basic qualification
    '3,4': 2,   # medium: secondary/technical qualification
    '5':   3    # high: university entrance qualification
}, new_name='educ3')
# ✅ recode: educ → educ3 (3471 assigned, 3 unassigned, 6 NaN)
```

### Creating Age Categories

```python
A18N = sis.recode(A18N, 'age', {
    '18-34': 1,   # Young adults
    '35-54': 2,   # Middle-aged
    '55-99': 3    # Older adults
}, new_name='age3')
```

### Creating Income Groups

```python
A18N = sis.recode(A18N, 'inc', {
    '>0 and <1000':     1,   # Low income
    '>=1000 and <2500': 2,   # Middle income
    '>=2500':           3    # High income
}, new_name='inc3')
```

### Reversing a Likert Scale (pv19)

```python
# pv19: 1=VERY UNLIKELY to 10=VERY LIKELY (voting CDU/CSU)
# Reverse so higher values = stronger CDU/CSU rejection
A18N = sis.recode(A18N, 'pv19', {
    1: 10, 2: 9, 3: 8, 4: 7, 5: 6,
    6: 5,  7: 4, 8: 3, 9: 2, 10: 1
}, new_name='pv19_r')
```

---

## 4. Frequency Tables

### Gender (fre)

```python
sis.fre(A18N, 'sex', sort=True, round_digits=2)
```

```
  Ausprägung  Häufigkeiten Prozent kum. Prozente gültigeP kum.gültigeP
0        1.0          1773   50.99         50.99    50.99        50.99
1        2.0          1704   49.01         100.0    49.01        100.0
2      Summe          3477     ---           ---      ---          ---
3     n-nan=          3477     ---           ---      ---          ---
```

**Interpretation:** 50.99% male (1.0), 49.01% female (2.0), no missing values

### Educational Attainment with Labels (fre_wl)

```python
sis.fre_wl(A18N, 'educ', A18L, sort_by_value=True, round_digits=2)
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
```

### CDU/CSU Voting Probability (pv19) with Labels

```python
sis.fre_wl(A18N, 'pv19', A18L, sort_by_value=True, round_digits=2)
```

```
   Ausprägung          Label  Häufigkeiten  Prozent  gültigeP kum.gültigeP
0         1.0  VERY UNLIKELY           651    18.72     18.72        18.72
...
9        10.0    VERY LIKELY           577    16.59     16.59       100.00
10        NaN            ---           184     5.29       ---          ---
```

**Interpretation:** Strong bimodal distribution – many respondents
rate CDU/CSU voting as very unlikely (18.72%) or very likely (16.59%)

---

## 5. Univariate Analysis

### Income (metric variable)

```python
sis.uniV(A18N, 'inc').summary()
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

**Key findings:**
- Median (€1,500) substantially below mean (€1,825.89) → right-skewed distribution
- High skewness (2.95) and kurtosis (19.01): income is **not normally distributed**
- 95% CI for the mean: [€1,779.31; €1,872.47]

### With Standard Errors

```python
sis.uniV(A18N, 'inc', se=True).summary()
```

Adds an `SE` column for mean, variance, SD, skewness, and kurtosis.

---

## 6. Bivariate Analysis: Cross-Tabulations

### Gender × Region (East/West)

```python
ct = sis.cross_tab(A18N, 'sex', 'eastwest')
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

**Interpretation:** Gender distribution nearly identical in West (1.0) and
East (2.0). Standardized residuals < |2| → no significant deviation from
independence.

### Accessing Individual Tables

```python
ct['observed']         # pd.DataFrame
ct['col_percent']      # pd.DataFrame
ct['st_residuals']     # pd.DataFrame
ct.keys()              # All available keys
```

---

## 7. Bivariate Analysis: Association Measures

### Nominal: Gender × Region

```python
sis.biV(A18N, "eastwest", "sex", scale="nominal").summary()
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

**Interpretation:** No significant association between gender and region
(Chi² not significant, Phi = 0.007 ≈ 0)

### Ordinal: Region × CDU/CSU Voting Probability

```python
sis.biV(A18N, "eastwest", "pv19", scale="ordinal").summary()
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

**Interpretation:** Significant negative association – West Germans (1)
tend to have higher CDU/CSU voting probability. Weak effect (r = –0.10).

### Statistics Only (without cross-table)

```python
sis.biV(A18N, "eastwest", "sex", scale="nominal",
        notable=True).summary()
```

---

## 8. T-Test

### Income Differences by Gender (without weighting)

```python
sis.ttest_u(group='sex', g1=1.0, g2=2.0,
            dependent='inc', data=A18N).summary()
```

```
============================================================
  T-Test: inc nach sex (1.0 vs. 2.0)
============================================================
  Test: Welch-t-Test (keine Varianzhomogenität)
  Gewichtung: keine
------------------------------------------------------------
       t-Statistik  18.274488
            p-Wert  0.00e+00   ***
                df  2639.2449
     Mittelwert G1  2212.972739
     Mittelwert G2  1403.182003
 Differenz (G1-G2)   809.790736
      95%-KI unten   722.899717
       95%-KI oben   896.681754
         Cohen's d     0.6439
          Levene p   6.84e-25   Welch-t-Test
============================================================
```

**Interpretation:**
- Men (G1=1.0) earn on average **€809.79 more** than women (G2=2.0)
- Highly significant difference (p < 0.001)
- **Medium to large effect**: Cohen's d = 0.64
- 95% CI of the difference: [€722.90; €896.68]

### With Survey Weighting

```python
sis.ttest_u(group='sex', g1=1.0, g2=2.0,
            dependent='inc', data=A18N, weight='wghtpew').summary()
```

```
       t-Statistik  18.793315
            p-Wert  0.00e+00   ***
     Mittelwert G1  2308.936567
     Mittelwert G2  1417.005032
 Differenz (G1-G2)   891.931534
         Cohen's d     0.6928
        n G1 (eff)    1474.97
        n G2 (eff)    1344.35
```

**Comparison unweighted vs. weighted:**

| | Unweighted | Weighted |
|-|-----------|---------|
| Mean men | €2,212.97 | €2,308.94 |
| Mean women | €1,403.18 | €1,417.01 |
| Difference | €809.79 | €891.93 |
| Cohen's d | 0.64 | 0.69 |

---

## 9. Regression

### OLS Regression: Income by Gender, Region and Education

```python
sis.regress('inc ~ sex + eastwest + iscd11', data=A18N).summary()
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

**Interpretation:**
- `sex` (b = –720.77, β = –0.27): Men earn on average **€720.77 more**,
  controlling for region and education
- `eastwest` (b = –395.87, β = –0.14): West Germans earn **€395.87 more**
  than East Germans
- `iscd11` (b = 288.15, β = 0.39): Strongest effect – income increases
  by **€288.15 per ISCED level**
- R² = 0.2649: The model explains **26.49%** of income variance

### With Weighting and Robust Standard Errors

```python
sis.regress('inc ~ sex + eastwest + iscd11', data=A18N,
            weight='wghtpew', robust=True).summary()
```

```
  Methode: WLS (Gewichtung: wghtpew)
  R²: 0.2683
      sex -791.9079  42.2564  -0.2902 -18.7405  2.71e-74  ***
 eastwest -394.3697  55.1926  -0.1102  -7.1453  1.12e-12  ***
   iscd11  293.8423  11.7433   0.3874  25.0222 6.04e-126  ***
```

### With Categorical Variable

```python
sis.regress('inc ~ sex + eastwest + C(iscd11)', data=A18N).summary()
```

```
  R²: 0.2859
C(iscd11)[T.2.0]  415.4761  ...  n.s.   VIF  8.24 ⚠️
C(iscd11)[T.7.0] 1813.1817  ...  ***   VIF 20.13 ⚠️
C(iscd11)[T.8.0] 3127.2537  ...  ***   VIF  3.54
```

### Standardized Coefficients (beta)

```python
sis.beta('inc ~ sex + eastwest + iscd11', data=A18N, full=True).summary()
```

```
  R²: 0.2649    R² (adj.): 0.2642    F: 369.9325  ***
------------------------------------------------------------
Variable Beta (β) SE (β)        t   p-Wert Sig.  r(y,x)
     sex  -0.2726 0.0155 -17.5814 0.00e+00  *** -0.3078
eastwest  -0.1400 0.0155  -9.0569 0.00e+00  *** -0.1451
  iscd11   0.3898 0.0155  25.1399 0.00e+00  ***  0.4123
```

### Accessing the statsmodels Object

```python
result = sis.regress('inc ~ sex + eastwest + iscd11', data=A18N)
result['model'].summary()          # Original statsmodels output
result['model'].resid              # Residuals as pd.Series
result['model'].fittedvalues       # Fitted values
result['anova']                    # Type 2 ANOVA table
```

---

## 10. Reliability Analysis

### Cronbach's Alpha for Reunification Scale

```python
sis.cronbach(A18N, ['pr04', 'pr05', 'pr07']).summary()
```

```
============================================================
  Reliabilitätsanalyse (3 Items)
============================================================
  Cronbach's Alpha: -0.2415
  Bewertung: inakzeptabel
  Items: 3
  n (Listwise): 3055
------------------------------------------------------------
Item    M   SD   r(it) Alpha ohne   Empfehlung
pr04 2.20 0.89 -0.1053    -0.1369 ⚠️ entfernen
pr05 1.95 0.83 -0.0987    -0.1591 ⚠️ entfernen
pr07 3.20 0.78 -0.1017    -0.1501 ⚠️ entfernen
============================================================
```

**Interpretation:** Negative alpha shows these items do not measure a
common dimension. pr04/pr05 (reunification advantages) and pr07 (feeling
like strangers) measure different concepts.

---

## 11. Effect Sizes

### Cohen's d for Income Difference

```python
sis.effect_size('cohen_d',
                m1=2212.97, m2=1403.18,
                sd1=1519.41, sd2=887.76,
                n1=1614, n2=1478).summary()
```

```
      Maß   Wert Bewertung
Cohen's d 0.6439    mittel
r (aus d) 0.3066       ---
```

### Converting Correlation to Cohen's d

```python
sis.effect_size('r_to_d', r=0.10).summary()
# → r → d: 0.2010  (r = 0.1000)
```

### Odds Ratio

```python
sis.effect_size('odds_ratio', a=30, b=10, c=20, d=40).summary()
# → Odds Ratio: 6.00, 95% CI: [2.25, 16.00]
```

---

## 12. Normality Tests

### Testing Income for Normality

```python
sis.normality_test(A18N, 'inc').summary()
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

**Conclusion:** Income is strongly right-skewed and not normally distributed
– for parametric tests, robust methods should be used (Welch t-test,
robust SEs in regression).

---

## 13. Group Comparison

### Mean Comparison: Men vs. Women

```python
sis.compare_groups(A18N, 'sex', ['inc', 'age', 'educ']).summary()
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

**Interpretation:**
- Men earn substantially more (€2,212.97 vs. €1,403.18)
- Age and education are virtually identical between groups
- Men have much higher income variance (SD: 1519 vs. 888)

---

## 14. Export

### Excel Export

```python
result = sis.regress('inc ~ sex + eastwest + iscd11', data=A18N)
sis.export_results(result, 'regression_result')
# ✅ Exported: regression_result.xlsx (3 sheets)
```

### LaTeX Export for Academic Papers

```python
sis.export_results(result, 'regression_result', format='latex')
# ✅ Exported: regression_result.tex
```

### CSV Export

```python
sis.export_results(result, 'regression_result', format='csv', decimal='.')
# ✅ Exported: regression_result_Statistiken.csv
```

---

## 15. Complete Analysis Workflow

### Research Question: What Explains Income Differences?

```python
# === STEP 1: Load Data ===
import pandas as pd
import cheatstat as sis

A18N = pd.read_spss('ALLBUS2018.sav',
    usecols=["sex", "inc", "eastwest", "iscd11", "educ", "wghtpew"],
    convert_categoricals=False)

# === STEP 2: Check Data Quality ===
sis.missing_report(A18N).summary()

# === STEP 3: Explore Variables ===
sis.uniV(A18N, 'inc').summary()
sis.uniV(A18N, 'sex').summary()
sis.uniV(A18N, 'eastwest').summary()

# === STEP 4: Check Normality ===
sis.normality_test(A18N, 'inc').summary()

# === STEP 5: Bivariate Associations ===
# Gender × Income (T-Test)
sis.ttest_u(group='sex', g1=1.0, g2=2.0,
            dependent='inc', data=A18N).summary()

# Region × Income (T-Test)
sis.ttest_u(group='eastwest', g1=1.0, g2=2.0,
            dependent='inc', data=A18N).summary()

# Education × Income (Correlation)
sis.biV(A18N, 'iscd11', 'inc', scale='ordinal',
        notable=True).summary()

# === STEP 6: Descriptive Group Comparison ===
sis.compare_groups(A18N, 'sex', ['inc', 'iscd11']).summary()

# === STEP 7: Multivariate Regression ===
result = sis.regress(
    'inc ~ sex + eastwest + iscd11',
    data=A18N,
    weight='wghtpew',
    robust=True
)
result.summary()

# === STEP 8: Effect Sizes ===
sis.effect_size('cohen_d',
                m1=2309, m2=1417,
                sd1=1519, sd2=888).summary()

# === STEP 9: Export Results ===
sis.export_results(result, 'income_analysis_final')
```

---

*cheatstat Version 4.1.2 | Author: Jürgen Leibold | March 2026*

[→ API Reference](api.md) |
[← Basic Usage](usage.md) |
[← Back to Overview](index.md)