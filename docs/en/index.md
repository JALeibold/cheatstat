# cheatstat: Simple Statistical Functions for Social Scientists

**A comprehensive documentation for students and researchers**

[![PyPI](https://img.shields.io/pypi/v/cheatstat?logo=pypi)](https://pypi.org/project/cheatstat/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)

---

## ⚠️ IMPORTANT NOTE ON WEIGHTING

> This implementation is an **approximation**. For scientific publications,
> the complete survey design (PSU, Strata) must be considered.

cheatstat provides simplified weighting suitable for **exploratory analyses and
teaching purposes**. However, it does **not** account for the complete survey
design (Primary Sampling Units, Strata) required for correct standard errors and
confidence intervals in complex survey data like the ALLBUS.

**For scientific publications, please use:**
- R packages like `survey` or `srvyr`
- SAS procedures like `SURVEYMEANS` or `SURVEYREG`
- SPSS modules like *Complex Samples*

| cheatstat is **not** for | cheatstat is **ideal** for |
|--------------------------|------------------------------|
| Official statistical reports | Social science courses |
| Scientific publications | Exploratory data analysis |
| Political decision-making | Quick hypothesis testing |
| | Introduction to statistical methods |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation and First Steps](#2-installation-and-first-steps)
3. [Data Preparation](#3-data-preparation)
   - [Missing Value Analysis](#31-missing-value-analysis-missing_report)
   - [Recoding Variables](#32-recoding-variables-recode)
4. [Descriptive Statistics](#4-descriptive-statistics)
   - [Frequency Tables](#41-frequency-tables-fre-and-fre_wl)
   - [Univariate Analysis](#42-univariate-analysis-univ)
5. [Bivariate Analysis](#5-bivariate-analysis)
   - [Cross-Tabulations](#51-cross-tabulations-cross_tab)
   - [Association Measures](#52-association-measures-biv)
   - [T-Test](#53-t-test-ttest_u)
6. [Multivariate Analysis](#6-multivariate-analysis)
   - [Regression](#61-regression-regress)
   - [Standardized Coefficients](#62-standardized-coefficients-beta)
   - [Reliability Analysis](#63-reliability-analysis-cronbach)
7. [Effect Sizes and Diagnostics](#7-effect-sizes-and-diagnostics)
   - [Effect Sizes](#71-effect-sizes-effect_size)
   - [Normality Tests](#72-normality-tests-normality_test)
   - [Group Comparison](#73-descriptive-group-comparison-compare_groups)
8. [Exporting Results](#8-exporting-results-export_results)
9. [Dummy Variables](#9-dummy-variables-create_dummies)
10. [Typical Workflows](#10-typical-workflows)
11. [Quick Reference](#11-quick-reference)
12. [Appendix](#12-appendix)

---

## 1. Introduction

**cheatstat** is a Python package specifically developed for students and
researchers in the social sciences. It simplifies the execution of basic
statistical analyses with survey data such as the ALLBUS, GESIS social surveys,
or other representative population surveys.

### Why cheatstat?

Social scientists often face the following challenges:

- **Complex survey weighting**: Many packages ignore survey weighting or
  implement it incompletely
- **Recoding variables**: Often cumbersome in Python, especially with
  complex conditions
- **Interpreting results**: Statistical outputs are often too technical
  for beginners
- **Reporting**: Results need to be in a format suitable for social
  science publications

### Overview of All Functions

| Function | Description |
|----------|-------------|
| `missing_report(df)` | Missing value analysis |
| `recode(df, col, mapping)` | Recode variables |
| `fre(df, col)` | Frequency table |
| `fre_wl(df, col, labels)` | Frequency table with value labels |
| `uniV(df, col)` | Univariate analysis (frequencies + statistics) |
| `cross_tab(df, col1, col2)` | Cross-tabulation |
| `biV(df, col1, col2, scale)` | Bivariate analysis with association measures |
| `ttest_u(group, g1, g2, dependent, data)` | Independent t-test |
| `regress(formula, data)` | OLS regression with beta coefficients |
| `beta(formula, data)` | Standardized regression coefficients |
| `cronbach(df, items)` | Reliability analysis (Cronbach's alpha) |
| `effect_size(type, ...)` | Effect size calculator |
| `normality_test(df, col)` | Normality tests |
| `compare_groups(df, group, vars)` | Descriptive group comparison |
| `export_results(result, file)` | Export results |
| `create_dummies(df, col)` | Create dummy variables |
| `help_cheatstat()` | Quick reference guide |

---

## 2. Installation and First Steps

### Installation

```bash
pip install cheatstat
```

For full functionality (especially regression), it is recommended to
additionally install statsmodels:

```bash
pip install statsmodels
```

### Import

After installation, you can import cheatstat as follows:

```python
import cheatstat as cs
```

> This is the recommended import method. All functions are then available
> under the prefix `cs.`.

### Loading ALLBUS Sample Data

The following examples use the ALLBUS 2018/2019, available from the
[GESIS website](https://www.gesis.org/allbus).

```python
import pandas as pd
import pyreadstat

# Load raw data (numeric values)
A18N = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "isco08", "eastwest", "iscd11",
             "lm02", "age", "scage", "educ", "pv19",
             "pr04", "pr05", "pr07", "wghtpew"],
    convert_categoricals=False
)

# Load data with value labels
A18L = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "isco08", "eastwest", "iscd11",
             "lm02", "age", "scage", "educ", "pv19",
             "pr04", "pr05", "pr07", "wghtpew"],
    convert_categoricals=True
)
```

> **Note**: `A18N` contains numeric values (e.g. `1.0` for male), while
> `A18L` contains value labels (e.g. `"MALE"`). Both DataFrames are
> needed for `fre_wl()` and `recode()`.

---

## 3. Data Preparation

### 3.1 Missing Value Analysis: `missing_report()`

Before beginning analysis, always get an overview of missing values.

```python
cs.missing_report(A18N).summary()
```

**Output:**
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
- `scage` (partner's age) has 44.90% missing – applies only to married
  respondents
- `inc` (income) has 11.07% missing – requires critical examination
- `eastwest`, `sex` and `wghtpew` are complete

**Status indicator:**

| Symbol | Meaning |
|--------|---------|
| ✅ | No missing values |
| 🟢 | Below threshold (< 5%) |
| 🟡 | Above threshold (5–10%) |
| 🔴 | Critical (> 10%) |

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `threshold` | float | 5.0 | Warning threshold in percent |

---

### 3.2 Recoding Variables: `recode()`

The `recode()` function supports diverse condition formats:

| Format | Example | Meaning |
|--------|---------|---------|
| Comma-separated values | `'1,2,4'` | Exactly these values |
| Range | `'1-6'` | All values from 1 to 6 |
| Greater than | `'>5'` | Values greater than 5 |
| Less than or equal | `'<=3'` | Values less than or equal to 3 |
| AND | `'>=2 and <=6'` | Values between 2 and 6 |
| OR | `'<2 or >8'` | Values below 2 or above 8 |
| NOT | `'not 5'` | All values except 5 |
| ELSE | `'else'` | All remaining values |
| Tuple | `(1, 6)` | Range 1 to 6 |
| Single number | `5` | Exactly value 5 |

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `column` | str | – | Source column name |
| `mapping` | dict | – | Mapping table |
| `new_name` | str | None | Target column name (None = overwrite) |
| `else_value` | any | NaN | Value for unassigned cases |

**Example 1: Collapsing education categories**

```python
# Original coding:
# 1 = NO CERTIFICATE  2 = LOWEST LEVEL     3 = INTERMEDIARY LEVEL
# 4 = QUALI.UNIV.APPL.SCI.  5 = QUALI.FOR UNIVERSITY
# 6 = OTHER SCHOOL CERTIF.  7 = STILL AT SCHOOL

A18N = cs.recode(A18N, 'educ', {
    '1,2': 1,   # low
    '3,4': 2,   # medium
    '5':   3    # high
}, new_name='educ3')
# ✅ recode: educ → educ3 (3471 assigned, 3 unassigned, 6 NaN)
```

**Example 2: Creating age categories**

```python
A18N = cs.recode(A18N, 'age', {
    '18-29': 1,   # young
    '30-49': 2,   # middle
    '50-99': 3    # older
}, new_name='age_kat')
```

**Example 3: Complex conditions**

```python
# Income tertiles
A18N = cs.recode(A18N, 'inc', {
    '<1000':            1,   # lower tertile
    '>=1000 and <2000': 2,   # middle tertile
    '>=2000':           3    # upper tertile
}, new_name='inc_kat')
```

**Example 4: Reversing a Likert scale**

```python
# pv19: 1 = VERY UNLIKELY ... 10 = VERY LIKELY
# Reverse so that higher values = stronger CDU/CSU rejection
A18N = cs.recode(A18N, 'pv19', {
    1: 10, 2: 9, 3: 8, 4: 7, 5: 6,
    6: 5,  7: 4, 8: 3, 9: 2, 10: 1
}, new_name='pv19_r')
```

> **Practical tip:** Always use `new_name` to preserve the original
> variable. Document every recoding in your analysis protocol.

---

## 4. Descriptive Statistics

### 4.1 Frequency Tables: `fre()` and `fre_wl()`

#### `fre()` – Simple Frequency Table

```python
cs.fre(A18N, 'sex', sort=True, round_digits=2)
```

**Output:**
```
  Ausprägung  Häufigkeiten Prozent kum. Prozente gültigeP kum.gültigeP
0        1.0          1773   50.99         50.99    50.99        50.99
1        2.0          1704   49.01         100.0    49.01        100.0
2      Summe          3477     ---           ---      ---          ---
3     n-nan=          3477     ---           ---      ---          ---
```

**Output columns:**

| Column | Meaning |
|--------|---------|
| `Ausprägung` | Value of the variable |
| `Häufigkeiten` | Absolute frequency |
| `Prozent` | Share of all cases (incl. missing) |
| `kum. Prozente` | Cumulative percentage |
| `gültigeP` | Share of valid cases only |
| `kum.gültigeP` | Cumulative valid percentage |

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `column` | str | – | Column name |
| `weight` | str/pd.Series | None | Weighting |
| `sort` | bool | True | Sort by value |
| `round_digits` | int | 2 | Decimal places |

#### `fre_wl()` – Frequency Table with Value Labels

Requires two DataFrames: numeric values (`A18N`) and labels (`A18L`).

```python
cs.fre_wl(A18N, 'educ', A18L, sort_by_value=True, round_digits=2)
```

**Output:**
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
- Largest group (34.37%) has `INTERMEDIARY LEVEL` (secondary school)
- 30.92% have `QUALI.FOR UNIVERSITY` (A-level equivalent)
- 23.30% have `LOWEST LEVEL` (basic secondary)
- Only 1.44% have `NO CERTIFICATE`

---

### 4.2 Univariate Analysis: `uniV()`

Performs a comprehensive analysis: frequency table + descriptive statistics.

```python
result = cs.uniV(A18N, 'inc', se=False)
result.summary()
```

**Output:**
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
- Median (€1,500) is substantially below the mean (€1,825.89) → right-skewed
  distribution typical for income
- Strong skewness (2.95) and high kurtosis (19.01): income is **not normally
  distributed**
- 95% CI for the mean: [€1,779.31; €1,872.47]
- Large IQR (€1,300) indicates high dispersion

**With standard errors:**

```python
cs.uniV(A18N, 'inc', se=True).summary()
```

Adds an `SE` column for mean, variance, SD, skewness, and kurtosis.

**Accessing result tables:**

```python
result = cs.uniV(A18N, 'inc')
result['fre']    # Frequency table as DataFrame
result['stats']  # Descriptive statistics as DataFrame
result.keys()    # All available keys
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `column_name` | str | – | Column name |
| `weight` | str/pd.Series | None | Weighting |
| `se` | bool | False | Show standard errors |

**Example: Political orientation (pv19)**

```python
cs.uniV(A18N, 'pv19').summary()
```

```
             Statistik    Wert
                 Modus     1.0
  50%-Quantil (Median)    6.00
            Mittelwert  5.5991
               Schiefe -0.1081
              Kurtosis -1.4303
```

**Interpretation:**
- Median = 6.0, mean = 5.60 → approximately symmetric distribution
- Mode at 1.0 (VERY UNLIKELY): many respondents strongly reject CDU/CSU

---

## 5. Bivariate Analysis

### 5.1 Cross-Tabulations: `cross_tab()`

```python
ct = cs.cross_tab(A18N, 'sex', 'eastwest')
ct.summary(show_tables=True)
```

**Output:**
```
============================================================
  Kreuztabelle: sex × eastwest
============================================================
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

--- st_residuals ---
eastwest   1.0   2.0
sex
1.0       0.17 -0.25
2.0      -0.17  0.25
============================================================
```

**Interpretation:**
- The gender distribution in West (1.0) and East (2.0) is nearly identical
  (51.24% vs. 50.46% male)
- Standardized residuals < |2.0| → no significant association

**Available tables in the result:**

| Key | Content |
|-----|---------|
| `observed` | Observed frequencies |
| `col_percent` | Column percentages |
| `row_percent` | Row percentages |
| `total_percent` | Total percentages |
| `expected` | Expected frequencies |
| `residuals` | Simple residuals |
| `st_residuals` | Standardized residuals |
| `deff` | Design effect (only with weighting) |
| `p_value_deff` | Corrected p-value (only with weighting) |

```python
ct['observed']      # Observed frequencies as DataFrame
ct['col_percent']   # Column percentages as DataFrame
ct.keys()           # All available keys
```

---

### 5.2 Association Measures: `biV()`

```python
# Nominal scale: Chi², G², Phi / Cramér's V
cs.biV(A18N, "eastwest", "sex", scale="nominal").summary()
```

**Output:**
```
============================================================
  Bivariate Analyse: eastwest × sex (nominal)
============================================================
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
- Chi² and G² are not significant (p > 0.05)
- Phi (φ) = 0.0066 → no association
- Gender and region (East/West) are statistically independent

```python
# Ordinal-metric scale: Pearson-r, Spearman, Kendall, Somers' D
cs.biV(A18N, "eastwest", "pv19", scale="ordinal").summary()
```

**Output:**
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

**Interpretation:**
- All measures are negative and highly significant (p < 0.001)
- East Germans (eastwest=1) tend towards lower pv19 values (lower CDU/CSU
  voting probability)
- The association is weak (r = –0.10)

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `col1`, `col2` | str | – | Column names |
| `scale` | str | – | `'nominal'`/`'n'` or `'ordinal'`/`'om'` |
| `weight` | str/pd.Series | None | Weighting |
| `notable` | bool | False | Statistics only, no cross-table |

**Scale aliases:**

| Accepted values | Internal |
|----------------|---------|
| `'nominal'`, `'n'`, `'kategorial'`, `'kat'` | Nominal |
| `'ordinal'`, `'om'`, `'metrisch'`, `'ordinal-metrisch'` | Ordinal-metric |

---

### 5.3 T-Test: `ttest_u()`

```python
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N).summary()
```

**Output:**
```
============================================================
  T-Test: inc nach sex (1.0 vs. 2.0)
============================================================
  Test: Welch-t-Test (keine Varianzhomogenität)
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
         Cohen's d                                  0.6439          ---
          Levene p                                6.84e-25 Welch-t-Test
============================================================
```

**Interpretation:**
- Men (G1=1.0) earn on average **€809.79 more** than women (G2=2.0)
- Difference is highly significant (p < 0.001)
- Effect size: Cohen's d = 0.64 → **medium to large effect**
- 95% CI of the difference: [€722.90; €896.68]
- Levene test: p < 0.001 → unequal variances → Welch t-test is correct

**With survey weighting:**

```python
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N, weight='wghtpew').summary()
```

**Comparison (unweighted vs. weighted):**

| | Unweighted | Weighted |
|-|-----------|---------|
| Difference | €809.79 | €891.93 |
| Cohen's d | 0.64 | 0.69 |
| n (eff) G1 | 1614 | 1474.97 |

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `group` | str | – | Grouping variable name |
| `g1`, `g2` | any | – | Group values |
| `dependent` | str | – | Dependent variable |
| `data` | pd.DataFrame | – | Input data |
| `weight` | str/pd.Series | None | Weighting |
| `levene_test` | str | `'median'` | Type of Levene test |
| `autoLevene` | bool | True | Automatic test selection |

---

## 6. Multivariate Analysis

### 6.1 Regression: `regress()`

```python
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N).summary()
```

**Output:**
```
============================================================
  Regression: inc ~ sex + eastwest + iscd11
============================================================
  Methode: OLS
  n (verwendet): 3083
  n (entfernt): 394
  R²: 0.2649    R² (adj.): 0.2642
  F: 369.9325   F p-Wert: 3.62e-205  ***
  AIC: 52115.94  BIC: 52140.07
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
- `sex` (b = –720.77, β = –0.27): Men (1) earn on average **€720.77 more**
  than women (2), controlling for region and education
- `eastwest` (b = –395.87, β = –0.14): West Germans (1) earn **€395.87 more**
  than East Germans (2)
- `iscd11` (b = 288.15, β = 0.39): Strongest effect – income increases
  by **€288.15 per ISCED level**
- R² = 0.2649: The model explains **26.49%** of income variance
- VIF < 2 for all predictors → **no multicollinearity**

**With weighting and robust standard errors:**

```python
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N,
           weight='wghtpew', robust=True).summary()
```

```
  Methode: WLS (Gewichtung: wghtpew)
  R²: 0.2683
      sex -791.9079  42.2564  -0.2902 -18.7405  2.71e-74  ***
 eastwest -394.3697  55.1926  -0.1102  -7.1453  1.12e-12  ***
   iscd11  293.8423  11.7433   0.3874  25.0222 6.04e-126  ***
```

**With categorical variable:**

```python
cs.regress('inc ~ sex + eastwest + C(iscd11)', data=A18N).summary()
```

```
  R²: 0.2859
C(iscd11)[T.2.0]  415.4761  ...  n.s.   VIF  8.24 ⚠️
C(iscd11)[T.7.0] 1813.1817  ...  ***   VIF 20.13 ⚠️
C(iscd11)[T.8.0] 3127.2537  ...  ***   VIF  3.54
```

> **Practical tip:** High VIF values (> 5: ⚠️, > 10: 🔴) indicate
> multicollinearity. This is common with categorical variables as the dummy
> variables are correlated.

**Accessing the statsmodels object:**

```python
result = cs.regress('inc ~ sex + eastwest + iscd11', data=A18N)
result['model'].summary()     # Original statsmodels output
result['model'].resid          # Residuals
result['model'].fittedvalues   # Fitted values
result['anova']                # ANOVA table
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `formula` | str | – | R-formula: `'y ~ x1 + x2 + ...'` |
| `data` | pd.DataFrame | – | Input data |
| `weight` | str | None | Weight column (WLS) |
| `robust` | bool | False | Robust SE (HC3) |
| `show_beta` | bool | True | Show standardized β |
| `show_ci` | bool | True | Show 95% CI |
| `show_vif` | bool | True | Show VIF |

---

### 6.2 Standardized Coefficients: `beta()`

```python
cs.beta('inc ~ sex + eastwest + iscd11', data=A18N, full=True).summary()
```

**Output:**
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
- `iscd11` has the strongest standardized effect (β = 0.39)
- `r(y,x)` = bivariate correlation without controlling for other variables
- Difference between β and r shows the influence of control variables

---

### 6.3 Reliability Analysis: `cronbach()`

```python
cs.cronbach(A18N, ['pr04', 'pr05', 'pr07']).summary()
```

**Output:**
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

**Interpretation:**
- Cronbach's Alpha = –0.24: **Unacceptable** – the items do not measure a
  common dimension
- All item-total correlations are negative – possible cause: pr04/pr05 ask
  about advantages (agree = positive), pr07 asks about feeling like strangers
  (agree = negative) → check scale direction!

**Alpha benchmarks:**

| Alpha | Rating |
|-------|--------|
| ≥ 0.90 | Excellent |
| ≥ 0.80 | Good |
| ≥ 0.70 | Acceptable |
| ≥ 0.60 | Questionable |
| ≥ 0.50 | Poor |
| < 0.50 | Unacceptable |

---

## 7. Effect Sizes and Diagnostics

### 7.1 Effect Sizes: `effect_size()`

```python
cs.effect_size('cohen_d', m1=2213, m2=1403, sd1=1519, sd2=888).summary()
```

**Output:**
```
============================================================
  Effektstärke: cohen_d
------------------------------------------------------------
      Maß   Wert Bewertung
Cohen's d 0.6439    mittel
r (aus d) 0.3066       ---
============================================================
```

**Available types:**

| Type | Required parameters | Description |
|------|--------------------|----|
| `'cohen_d'` | `m1, m2, sd1, sd2` (opt: `n1, n2`) | Cohen's d |
| `'eta_sq'` | `f, df1, df2` | Eta² |
| `'omega_sq'` | `f, df1, df2` (opt: `n`) | Omega² |
| `'r_to_d'` | `r` | Correlation → Cohen's d |
| `'d_to_r'` | `d` | Cohen's d → Correlation |
| `'odds_ratio'` | `a, b, c, d` | Odds ratio from 2×2 table |

```python
cs.effect_size('r_to_d', r=0.12).summary()
# → r → d: 0.2417  (r = 0.1200)

cs.effect_size('odds_ratio', a=30, b=10, c=20, d=40).summary()
# → Odds Ratio: 6.00, 95% CI: [2.25, 16.00]
```

---

### 7.2 Normality Tests: `normality_test()`

```python
cs.normality_test(A18N, 'inc').summary()
```

**Output:**
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

**Interpretation:**
- Both tests significant (p < 0.001) → clear deviation from normal distribution
- Right-skewed income distributions are typical
- With n > 500, normality tests are very sensitive – graphical inspection
  additionally recommended

---

### 7.3 Descriptive Group Comparison: `compare_groups()`

```python
cs.compare_groups(A18N, 'sex', ['inc', 'age', 'educ']).summary()
```

**Output:**
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
- Clear income gap: men earn €809 more on average
- Age and education are almost identical between groups

---

## 8. Exporting Results: `export_results()`

```python
result = cs.regress('inc ~ sex + eastwest + iscd11', data=A18N)
cs.export_results(result, 'regression_result', format='excel')
# ✅ Exported: regression_result.xlsx (3 sheets)
```

**Supported formats:**

| Format | Extension | Use case |
|--------|-----------|----------|
| `'excel'` | `.xlsx` | Microsoft Excel, LibreOffice Calc |
| `'csv'` | `.csv` | Spreadsheets, R, SPSS |
| `'html'` | `.html` | Web presentations, reports |
| `'latex'` | `.tex` | Scientific publications |

```python
cs.export_results(result, 'result', format='latex')
# ✅ Exported: result.tex
```

---

## 9. Dummy Variables: `create_dummies()`

```python
A18N = cs.create_dummies(A18N, 'educ', prefix='educ')
# Creates columns: educ_1, educ_2, educ_3, educ_4, educ_5, educ_6, educ_7
```

Dummy variables are appended directly to the DataFrame. Decimal points are
removed (e.g. `educ_3` instead of `educ_3.0`).

---

## 10. Typical Workflows

### Workflow 1: Descriptive Analysis of a Variable

```python
# Step 1: Check missing values
cs.missing_report(A18N).summary()

# Step 2: Frequency table with labels
cs.fre_wl(A18N, 'pv19', A18L, sort_by_value=True)

# Step 3: Descriptive statistics
cs.uniV(A18N, 'pv19', se=True).summary()

# Step 4: Check normality
cs.normality_test(A18N, 'pv19').summary()
```

### Workflow 2: Association Analysis

```python
# Step 1: Cross-tabulation with all tables
cs.cross_tab(A18N, 'eastwest', 'pv19').summary(show_tables=True)

# Step 2: Association measures
cs.biV(A18N, 'eastwest', 'pv19', scale='ordinal').summary()

# Step 3: Statistics only (no cross-table)
cs.biV(A18N, 'eastwest', 'pv19', scale='ordinal', notable=True).summary()
```

### Workflow 3: Regression

```python
# Step 1: Recode variables
A18N = cs.recode(A18N, 'educ', {'1,2': 1, '3,4': 2, '5': 3}, new_name='educ3')

# Step 2: OLS regression with weighting
result = cs.regress('inc ~ sex + eastwest + educ3',
                    data=A18N, weight='wghtpew', robust=True)
result.summary()

# Step 3: Export
cs.export_results(result, 'regression_inc', format='excel')
```

### Workflow 4: Reliability Analysis

```python
# Step 1: Inspect items
for item in ['pr04', 'pr05', 'pr07']:
    cs.uniV(A18N, item).summary()

# Step 2: Reliability analysis
cs.cronbach(A18N, ['pr04', 'pr05', 'pr07']).summary()
```

---

## 11. Quick Reference

```python
cs.help_cheatstat()
```

Prints a compact overview of all functions in the console.

---

## 12. Appendix

### ALLBUS Variable Reference (Version 2018/2019)

| Variable | Description | Scale level | Value range |
|----------|-------------|-------------|-------------|
| `sex` | Gender | nominal | 1=Male, 2=Female |
| `inc` | Monthly net income | metric | €25–18,000 |
| `eastwest` | Region | nominal | 1=West, 2=East |
| `iscd11` | Education (ISCED 2011) | ordinal | 1–8 |
| `lm02` | TV watching time/day (minutes) | metric | 1–1,200 |
| `age` | Age | metric | 18–95 years |
| `scage` | Partner's age | metric | 21–96 years |
| `educ` | School leaving certificate | ordinal | 1–7 |
| `pv19` | Probability of voting CDU/CSU | ordinal | 1–10 |
| `pr04` | Reunification: advantages for West | ordinal | 1–4 |
| `pr05` | Reunification: advantages for East | ordinal | 1–4 |
| `pr07` | Citizens feel like strangers in other part? | ordinal | 1–4 |
| `wghtpew` | Person weight | metric | 0.54–1.21 |

### Significance Stars

| Symbol | p-value | Interpretation |
|--------|---------|---------------|
| `***` | < 0.001 | Highly significant |
| `**` | < 0.01 | Significant |
| `*` | < 0.05 | Marginally significant |
| `n.s.` | ≥ 0.05 | Not significant |

### Effect Size Benchmarks (Cohen, 1988)

| Measure | Small | Medium | Large |
|---------|-------|--------|-------|
| Cohen's d | 0.20 | 0.50 | 0.80 |
| r | 0.10 | 0.30 | 0.50 |
| Eta² | 0.01 | 0.06 | 0.14 |
| Phi/Cramér's V | 0.10 | 0.30 | 0.50 |

### Common Error Messages

| Error message | Cause | Solution |
|--------------|-------|----------|
| `ValueError: Gewichtungsspalte '...' nicht gefunden` | Typo in column name | `print(df.columns)` |
| `ValueError: Gruppe '...' existiert nicht` | Wrong group type | `print(df['var'].unique())` |
| `LinAlgError: Singular matrix` | Multicollinearity | Remove redundant predictors |
| `cronbach(): Alpha negativ` | Inconsistent scale directions | Reverse items with `recode()` |

---

*cheatstat Version 4.1 | Author: Jürgen Leibold | March 2026*

[🇩🇪 Deutsche Dokumentation](../de/index.md) | [⬆️ Back to overview](../../README.md)