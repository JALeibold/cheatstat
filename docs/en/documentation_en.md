# cheatstat – Documentation (Version 4.1)

**Simple Statistical Functions for the Social Sciences**  
*Author: Jürgen Leibold | Version 4.1 | March 2026 | License: MIT*

---

> [!WARNING]
> ## ⚠️ Important Note on Weighting
>
> **This implementation is an approximation.**
>
> cheatstat provides **simplified weighting** suitable for exploratory analyses and teaching purposes. However, it does **not** account for the full survey design (Primary Sampling Units, Strata) required for correct standard errors and confidence intervals in complex survey data such as the ALLBUS.
>
> **cheatstat is NOT suitable for:**
> - Official statistical reports
> - Scientific publications
> - Policy decision-making
>
> **For scientific publications** please use:
> - R packages such as `survey` or `srvyr`
> - SAS procedures such as `SURVEYMEANS` or `SURVEYREG`
> - SPSS modules such as "Complex Samples"
>
> **cheatstat is ideal for:**
> - Courses in the social sciences
> - Exploratory data analysis
> - Quick hypothesis checking
> - Introduction to statistical methods

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation and Getting Started](#installation-and-getting-started)
3. [Preparing Data](#preparing-data)
   - [Loading Data](#loading-data)
   - [Analysing Missing Values – `missing_report()`](#analysing-missing-values--missing_report)
   - [Recoding Variables – `recode()`](#recoding-variables--recode)
4. [Descriptive Statistics](#descriptive-statistics)
   - [Frequency Tables – `fre()`](#frequency-tables--fre)
   - [Frequency Tables with Value Labels – `fre_wl()`](#frequency-tables-with-value-labels--fre_wl)
   - [Univariate Analysis – `uniV()`](#univariate-analysis--univ)
5. [Bivariate Analysis](#bivariate-analysis)
   - [Cross-tabulations – `cross_tab()`](#cross-tabulations--cross_tab)
   - [Association Measures – `biV()`](#association-measures--biv)
   - [T-Test – `ttest_u()`](#t-test--ttest_u)
6. [Multivariate Analysis](#multivariate-analysis)
   - [Regression – `regress()`](#regression--regress)
   - [Standardised Coefficients – `beta()`](#standardised-coefficients--beta)
   - [Reliability Analysis – `cronbach()`](#reliability-analysis--cronbach)
7. [Effect Sizes and Diagnostics](#effect-sizes-and-diagnostics)
   - [Computing Effect Sizes – `effect_size()`](#computing-effect-sizes--effect_size)
   - [Testing for Normality – `normality_test()`](#testing-for-normality--normality_test)
   - [Descriptive Group Comparison – `compare_groups()`](#descriptive-group-comparison--compare_groups)
8. [Exporting Results – `export_results()`](#exporting-results--export_results)
9. [Utility Functions](#utility-functions)
   - [`describe_df()`](#describe_df)
   - [`create_dummies()`](#create_dummies)
   - [`help_cheatstat()`](#help_cheatstat)
10. [Typical Workflows](#typical-workflows)
11. [Appendix](#appendix)
    - [ALLBUS Variable Reference](#allbus-variable-reference)
    - [Significance Stars](#significance-stars)
    - [Effect Size Benchmarks](#effect-size-benchmarks)
    - [Troubleshooting](#troubleshooting)

---

## Introduction

cheatstat is a Python package developed specifically for students and researchers in the social sciences. It simplifies the execution of basic statistical analyses with survey data such as the ALLBUS, GESIS social surveys, or other representative population surveys.

### Why cheatstat?

Social scientists often face the following challenges:

| Challenge | cheatstat's Solution |
|---|---|
| Complex survey weighting: many packages ignore survey weighting or implement it incompletely | Uniform handling of survey weighting across all functions (for exploratory purposes) |
| Recoding variables: often cumbersome in Python, especially with complex conditions | Intuitive recoding functions with support for complex conditions |
| Interpreting results: statistical output is often too technical for beginners | Clear, interpretable output with significance stars and evaluations |
| Reporting: results need to be in a format suitable for social science publications | Direct export to formats for scientific reports |

> *"cheatstat is not the most powerful statistics package for Python, but it is the best one for social scientists who need to work quickly and correctly – within the scope of exploratory analyses."*

---

## Installation and Getting Started

### Installation

cheatstat can be installed via pip:

```
pip install cheatstat
```

For full functionality (especially regression), it is recommended to additionally install `statsmodels`:

```
pip install statsmodels
```

**Dependencies:**

| Package | Type | Purpose |
|---|---|---|
| pandas | Required | Data processing |
| numpy | Required | Numerical computations |
| scipy | Required | Statistical tests |
| statsmodels | Optional | `regress()`, `beta()` |
| numba | Optional | Speed optimisation |

**System requirements:** Python ≥ 3.9

### Import

After installation, import cheatstat as follows:

```python
import cheatstat as sis
```

This is the recommended import method, as it makes all functions available under the `sis.` prefix and avoids conflicts with other packages.

---

## Preparing Data

### Loading Data

The following examples use the ALLBUS 2018/2019. The data can be downloaded from the GESIS website.

```python
import pandas as pd
import pyreadstat

# Load raw data (without categorical coding)
A18N = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "isco08", "eastwest", "iscd11", "lm02", "age",
             "scage", "educ", "pv19", "pr04", "pr05", "pr07", "wghtpew"],
    convert_categoricals=False
)

# Load data with value labels
A18L = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "isco08", "eastwest", "iscd11", "lm02", "age",
             "scage", "educ", "pv19", "pr04", "pr05", "pr07", "wghtpew"],
    convert_categoricals=True
)
```

> **Note:** `A18N` contains numeric values (e.g. `1.0` for male), while `A18L` contains categorical variables with value labels (e.g. `"MAENNLICH"`). This distinction is important for the functions `fre_wl()` and `recode()`.

---

### Analysing Missing Values – `missing_report()`

Before starting any analysis, you should always get an overview of missing values.

```python
sis.missing_report(A18N).summary()
```

```
============================================================
  Fehlende-Werte-Bericht
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
- The variable `scage` (spouse's age) has 44.90% missing values – this is critical
- The variable `inc` (income) has 11.07% missing values – this is critical
- The variables `pr04`, `pr05`, `pr07`, `lm02`, and `pv19` have between 5.29% and 8.66% missing values
- The variables `iscd11`, `age`, and `educ` have less than 1% missing values
- The variables `eastwest`, `sex`, and `wghtpew` are complete

**Practical Tips:**
- Variables with more than 10% missing values should be reviewed critically
- For critical variables such as `inc` (income), check whether the missing values are systematic
- For further analysis, you can either use listwise deletion or perform imputation

---

### Recoding Variables – `recode()`

In social science analyses, variables often need to be recoded in order to test hypotheses. The `recode()` function is highly flexible and supports:

| Syntax | Description | Example |
|---|---|---|
| `'1,2,4,6'` | Comma-separated values | Collapsing multiple categories |
| `'1-6'` | Ranges using a hyphen | Specifying a value range |
| `'>5'`, `'>=5'`, `'<3'` | Comparison operators | Threshold conditions |
| `'>2 and <8'` | Logical AND | Both conditions must hold |
| `'<2 or >8'` | Logical OR | At least one condition must hold |
| `'not 5'`, `'not 1,2,3'` | Negation | All values except those listed |
| `'else'` | Default value | All remaining values |

**Example 1: Simple recoding of education**

```python
# Original coding:
# 1 = NO CERTIFICATE, 2 = LOWEST LEVEL, 3 = INTERMEDIARY LEVEL
# 4 = QUALI.UNIV.APPL.SCI., 5 = QUALI.FOR UNIVERSITY
# 6 = OTHER SCHOOL CERTIF., 7 = STILL AT SCHOOL

A18N = sis.recode(A18N, 'educ', {
    '1,2': 1,  # low
    '3,4': 2,  # medium
    '5': 3     # high
}, new_name='educ3')
```

**Example 2: Creating age categories**

```python
A18N = sis.recode(A18N, 'age', {
    '18-29': 1,  # young
    '30-49': 2,  # middle-aged
    '50-99': 3   # older
}, new_name='age_kat')
```

**Example 3: Complex conditions**

```python
# Identifying East Germans (eastwest=1) with low income (inc<2000)
A18N = sis.recode(A18N, 'eastwest', {
    '1 and inc<2000': 1,  # East Germany with low income
    '1 and inc>=2000': 2, # East Germany with high income
    '2': 3                # West Germany
}, new_name='ostwest_eink')
```

**Example 4: Inverting a Likert scale**

```python
# pv19: Probability of voting CDU/CSU (1=VERY UNLIKELY, 10=VERY LIKELY)
# Inverting the scale for analysis purposes
A18N = sis.recode(A18N, 'pv19', {
    1: 10,
    2: 9,
    3: 8,
    4: 7,
    5: 6,
    6: 5,
    7: 4,
    8: 3,
    9: 2,
    10: 1
}, new_name='pv19_r')
```

**Example 5: Flagging missing values**

```python
# inc: Income – explicitly flag missing values
A18N = sis.recode(A18N, 'inc', {
    'not 0-18000': np.nan,  # All values outside the range treated as missing
    'else': 'inc'           # Keep all other values
}, new_name='inc_clean')
```

> **Practical Tips:**
> - Always use `new_name` to preserve the original variable
> - Document every recoding step in your analysis log
> - After recoding, verify the result using `uniV()`

---

## Descriptive Statistics

### Frequency Tables – `fre()`

Creates a weighted frequency table for a variable.

**Example: Frequency table for sex**

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

**Interpretation:**
- The variable `sex` has two categories: `1.0` (male) and `2.0` (female)
- 50.99% of respondents are male, 49.01% are female
- There are no missing values (`n-nan=` equals `n=`)

---

### Frequency Tables with Value Labels – `fre_wl()`

Creates a frequency table with value labels. Requires two DataFrames: one with numeric values (`A18N`) and one with labels (`A18L`).

**Example: Sex with labels**

```python
sis.fre_wl(A18N, "sex", A18L, sort_by_value=True, round_digits=2)
```

```
  Ausprägung   Label  Häufigkeiten Prozent kum. Prozente gültigeP kum.gültigeP
0        1.0    MALE          1773   50.99         50.99    50.99        50.99
1        2.0  FEMALE          1704   49.01         100.0    49.01        100.0
2      Summe     ---          3477     ---           ---      ---          ---
3     n-nan=     ---          3477     ---           ---      ---          ---
```

**Example: Educational attainment with labels**

```python
sis.fre_wl(A18N, "educ", A18L, sort_by_value=True, round_digits=2)
```

```
  Ausprägung                 Label  Häufigkeiten Prozent kum. Prozente gültigeP kum.gültigeP
0        1.0        NO CERTIFICATE           50      1.44        98.71     1.44        98.71
1        2.0          LOWEST LEVEL          809     23.30        88.58    23.30        88.58
2        3.0    INTERMEDIARY LEVEL         1190     34.37        34.37    34.37        34.37
3        4.0  QUALI.UNIV.APPL.SCI.          301      8.69        97.27     8.69        97.27
4        5.0  QUALI.FOR UNIVERSITY         1070     30.92        65.29    30.92        65.29
5        6.0  OTHER SCHOOL CERTIF.           20      0.58        99.91     0.58        99.91
6        7.0       STILL AT SCHOOL           22      0.63        99.34     0.63        99.34
7        NaN                   ---           11      0.32        99.68     0.32        99.68
8      Summe                   ---         3474     99.91        99.91    99.91        99.91
9     n-nan=                   ---         3463     99.68        99.68    99.68        99.68
```

**Interpretation:**
- 34.37% of respondents hold an INTERMEDIARY LEVEL qualification (equivalent to a secondary school certificate)
- 30.92% hold QUALI.FOR UNIVERSITY (equivalent to the Abitur / A-levels)
- 23.30% hold a LOWEST LEVEL qualification (equivalent to a basic school-leaving certificate)
- Only 1.44% have NO CERTIFICATE (no school-leaving qualification)

> **Practical Tip:** For Likert scales (e.g. `pv19`), `fre_wl()` is particularly useful because you can see the response categories directly.

---

### Univariate Analysis – `uniV()`

Performs a comprehensive univariate analysis, including a frequency table and descriptive statistics.

**Example: Income analysis**

```python
result = sis.uniV(A18N, 'inc', se=False)
result.summary()
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

**Interpretation:**
- The median income is 1,500 €, the mean is 1,825.89 €
- The 95% confidence interval for the mean is [1,779.31; 1,872.47]
- The distribution is strongly right-skewed (skewness = 2.95)
- Kurtosis is positive (19.01), indicating a more peaked distribution than the normal distribution
- High skewness and kurtosis suggest that the variable is not normally distributed

**With standard errors:**

```python
sis.uniV(A18N, 'inc', se=True).summary()
```

```
     Statistik        Wert  Standardfehler
0         Modus       2000.0           ---
1    25%-Quantil      1000.00           ---
...
5      Mittelwert     1825.89         22.82
6  95%-KI (untere Grenze)      1779.31           ---
...
10         Varianz  1744997.75       97.56
```

> **Practical Tip:** The standard error of the mean (22.82) indicates how precisely the sample mean estimates the population mean.

**Example: Political attitude (`pv19`)**

```python
sis.uniV(A18N, 'pv19', se=False).summary()
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
               Varianz 10.7846
    Standardabweichung  3.2840
               Schiefe -0.1081
              Kurtosis -1.4303
                Exzess   -4.43
============================================================
```

**Interpretation:**
- The median of the political attitude scale (probability of voting CDU/CSU) is 6.0
- The mean is 5.60
- The distribution is slightly left-skewed (skewness = −0.11)
- Kurtosis is negative (−1.43), indicating a flatter distribution than the normal distribution
- The distribution is approximately symmetric

---

## Bivariate Analysis

### Cross-tabulations – `cross_tab()`

Creates a weighted cross-tabulation with various percentage breakdowns and residuals.

**Example: Sex by region (East/West)**

```python
ct = sis.cross_tab(A18N, 'sex', 'eastwest')
ct.summary(show_tables=True)
```

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

--- total_percent ---
eastwest    1.0    2.0  Gesamt
sex
1.0       35.17  15.82   50.99
2.0       33.48  15.53   49.01
Gesamt    68.65  31.35  100.00

--- residuals ---
eastwest   1.0   2.0  Gesamt
sex
1.0       5.82 -5.82     NaN
2.0      -5.82  5.82     NaN
Gesamt     NaN   NaN     NaN

--- expected ---
eastwest      1.0     2.0  Gesamt
sex
1.0       1217.18  555.82     NaN
2.0       1169.82  534.18     NaN
Gesamt        NaN     NaN     NaN

--- st_residuals ---
eastwest   1.0   2.0  Gesamt
sex
1.0       0.17 -0.25     NaN
2.0      -0.17  0.25     NaN
Gesamt     NaN   NaN     NaN
============================================================
```

**Interpretation:**
- The observed frequencies (`observed`) show the distribution of respondents
- The column percentages (`col_percent`) show that East and West Germany have almost equal proportions of male and female respondents
- The residuals are small, indicating a weak association
- The chi-squared test confirms this (see `biV()` output)

---

### Association Measures – `biV()`

Performs a bivariate analysis and computes association measures based on the level of measurement.

**Example 1: Nominally scaled variables (East/West by sex)**

```python
sis.biV(A18N, "eastwest", "sex", scale="nominal").summary()
```

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
- Chi² and G² are not significant (p > 0.05)
- Phi (φ) is close to 0, indicating no association
- Sex and region (East/West) are independent

**Example 2: Ordinally scaled variables (East/West by political attitude)**

```python
sis.biV(A18N, "eastwest", "pv19", scale="ordinal").summary()
```

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
- All association measures are negative and statistically significant (p < 0.001)
- East Germans tend to have lower scores on `pv19` (lower probability of voting CDU/CSU)
- The association is weak (r = −0.10)
- Somers' D (Y|X) = −0.0571 means that predicting `pv19` from `eastwest` improves accuracy by 5.71%

> **Practical Tip:** For ordinally scaled variables like `pv19` (political attitude on a Likert scale), Spearman-Rho and Kendall's Tau-b are the most appropriate measures.

---

### T-Test – `ttest_u()`

Performs an independent-samples t-test for two groups.

**Example: Income differences by sex (unweighted)**

```python
sis.ttest_u(group='sex', g1=1.0, g2=2.0, dependent='inc', data=A18N).summary()
```

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
- The t-test is highly significant (p < 0.001); men earn on average 809.79 € more than women
- The effect is medium to large (Cohen's d = 0.64)
- The 95% confidence interval for the difference is [722.90; 896.68]
- The Levene test reveals significant differences in variances (p < 0.001), so the Welch t-test was applied
- Variance is considerably higher for men (2,308,618.97) than for women (788,126.64)

**With survey weighting:**

```python
sis.ttest_u(group='sex', g1=1.0, g2=2.0, dependent='inc',
            data=A18N, weight='wghtpew').summary()
```

```
============================================================
  T-Test: inc nach sex (1.0 vs. 2.0)
============================================================
  Test: Welch-t-Test
  Gruppen: 1.0 vs. 2.0
  AV: inc
  Gewichtung: wghtpew
------------------------------------------------------------
         Statistik           Wert Entscheidung
              Test   Welch-t-Test          ---
       t-Statistik      18.793315          ---
            p-Wert       0.00e+00          ***
                df      2419.2600          ---
     Mittelwert G1    2308.936567          ---
     Mittelwert G2    1417.005032          ---
 Differenz (G1-G2)     891.931534          ---
      95%-KI unten     798.865001          ---
       95%-KI oben     984.998068          ---
        Varianz G1 2411249.772976          ---
        Varianz G2  830366.671424          ---
         Cohen's d         0.6928          ---
        n G1 (roh)           1614          ---
        n G2 (roh)           1478          ---
        n G1 (eff)        1474.97          ---
        n G2 (eff)        1344.35          ---
          Levene p            --- Welch-t-Test
          Gruppe 1            1.0          ---
          Gruppe 2            2.0          ---
Abhängige Variable            inc          ---
============================================================
```

**Interpretation:**
- With weighting, the difference is even larger: men earn on average 891.93 € more
- The effect is slightly larger (Cohen's d = 0.69)
- The effective sample size is smaller than the raw sample size (1,474.97 vs. 1,614 for men)
- Weighting amplifies the difference, suggesting that the unweighted analysis underestimates it

> **Practical Tip:** With survey data such as the ALLBUS, you should always apply weighting to obtain representative results. Note, however, that cheatstat provides only simplified weighting.

---

## Multivariate Analysis

### Regression – `regress()`

Performs OLS regression and adds standardised beta coefficients to the output.

**Example: Income by sex, region and education (OLS, unweighted)**

```python
sis.regress('inc ~ sex + eastwest + iscd11', data=A18N).summary()
```

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
- The regression coefficient for `sex` is −720.77: men (1.0) earn on average 720.77 € more than women (2.0), controlling for region and education
- The coefficient for `eastwest` is −395.87: East Germans (1.0) earn on average 395.87 € less than West Germans (2.0)
- The coefficient for `iscd11` is 288.15: income increases by 288.15 € per education level
- All coefficients are highly significant (p < 0.001)
- The model explains 26.49% of the variance in income (R² = 0.2649)
- The standardised coefficient for `iscd11` (0.39) is the largest, indicating the strongest effect

**With weighting and robust standard errors:**

```python
sis.regress('inc ~ sex + eastwest + iscd11', data=A18N,
            weight='wghtpew', robust=True).summary()
```

```
============================================================
  Regression: inc ~ sex + eastwest + iscd11
============================================================
  Formel: inc ~ sex + eastwest + iscd11
  Methode: WLS (Gewichtung: wghtpew)
  n (verwendet): 3083
  n (original): 3477
  n (entfernt): 394
  R²: 0.2683
  R² (adj.): 0.2676
  F: 376.4310
  F p-Wert: 2.86e-208
  F Sig.: ***
  AIC: 52486.1500
  BIC: 52510.2800
  Durbin-Watson: 1.9853
  Gewichtung: wghtpew
  Robuste SE: HC3
------------------------------------------------------------
 Variable         b       SE Beta (β)        t    p-Wert Sig. 95%-KI unten 95%-KI oben  VIF
Intercept 2251.1708 107.5104      ---  20.9391  3.97e-91  ***    2040.3714   2461.9701  ---
      sex -791.9079  42.2564  -0.2902 -18.7405  2.71e-74  ***    -874.7615   -709.0543 1.01
 eastwest -394.3697  55.1926  -0.1102  -7.1453  1.12e-12  ***    -502.5879   -286.1516 1.00
   iscd11  293.8423  11.7433   0.3874  25.0222 6.04e-126  ***     270.8169    316.8678 1.01
============================================================
```

**Interpretation:**
- With weighting and robust standard errors, effects are slightly larger
- The gender effect increases from −720.77 to −791.91 €
- The East-West difference remains similar (−394.37 €)
- The model now explains 26.83% of variance (R² = 0.2683)

**With a categorical variable:**

```python
sis.regress('inc ~ sex + eastwest + C(iscd11)', data=A18N).summary()
```

```
============================================================
  Regression: inc ~ sex + eastwest + C(iscd11)
============================================================
  Formel: inc ~ sex + eastwest + C(iscd11)
  Methode: OLS
  n (verwendet): 3083
  n (original): 3477
  n (entfernt): 394
  R²: 0.2859
  R² (adj.): 0.2838
  F: 136.6752
  F p-Wert: 3.36e-217
  F Sig.: ***
  AIC: 52038.9400
  BIC: 52099.2800
  Durbin-Watson: 1.9695
------------------------------------------------------------
        Variable         b       SE Beta (β)        t   p-Wert Sig. 95%-KI unten 95%-KI oben      VIF
       Intercept 2346.0978 232.5945      ---  10.0866 1.47e-23  ***    1890.0414   2802.1543      ---
C(iscd11)[T.2.0]  415.4761 232.9468   0.0780   1.7836  0.07459 n.s.     -41.2712    872.2234  8.24 ⚠️
C(iscd11)[T.3.0]  721.0482 221.3832   0.2714   3.2570  0.00114   **     286.9741   1155.1222 29.88 ⚠️
C(iscd11)[T.4.0]  965.4742 231.4547   0.1909   4.1713  0.00003  ***     511.6525   1419.2959  9.02 ⚠️
C(iscd11)[T.5.0] 1186.6175 226.1818   0.3064   5.2463 1.66e-07  ***     743.1347   1630.1003 14.67 ⚠️
C(iscd11)[T.6.0] 1013.2220 239.1720   0.1581   4.2364  0.00002  ***     544.2687   1482.1753  5.99 ⚠️
C(iscd11)[T.7.0] 1813.1817 223.7406   0.5543   8.1039 7.60e-16  ***    1374.4854   2251.8780 20.13 ⚠️
C(iscd11)[T.8.0] 3127.2537 257.8673   0.3478  12.1274 4.26e-33  ***    2621.6440   3632.8634     3.54
             sex -718.2815  40.6943  -0.2717 -17.6507 1.73e-66  ***    -798.0723   -638.4907     1.02
        eastwest -393.4467  43.4451  -0.1391  -9.0562 2.34e-19  ***    -478.6311   -308.2622     1.02
============================================================
```

**Interpretation:**
- The reference category is `iscd11=1.0` (PRIMARY EDUCATION)
- Respondents with `iscd11=8.0` (DOCTORAL LEVEL) earn on average 3,127.25 € more than the reference group
- The VIF value for `iscd11=7.0` (MASTER LEVEL) is 20.13 – this indicates multicollinearity

> **Practical Tip:** VIF values (Variance Inflation Factor) indicate multicollinearity. Values above 5 (flagged in yellow) or 10 (flagged in red) are critical. For categorical variables such as `iscd11`, multicollinearity is common because categories are correlated.

---

### Standardised Coefficients – `beta()`

Computes only the standardised regression coefficients (useful for quick comparisons).

```python
sis.beta('inc ~ sex + eastwest + iscd11', data=A18N, full=True).summary()
```

```
============================================================
  Standardisierte Regression: inc ~ sex + eastwest + iscd11
============================================================
  Formel: inc ~ sex + eastwest + iscd11
  n: 3083
  n (eff): 3083.0000
  R²: 0.2649
  R² (adj.): 0.2642
  F: 369.9325
  F p: 1.11e-16
  F Sig.: ***
  Gewichtung: keine
------------------------------------------------------------
Variable Beta (β) SE (β)        t   p-Wert Sig.  r(y,x)
     sex  -0.2726 0.0155 -17.5814 0.00e+00  *** -0.3078
eastwest  -0.1400 0.0155  -9.0569 0.00e+00  *** -0.1451
  iscd11   0.3898 0.0155  25.1399 0.00e+00  ***  0.4123
============================================================
```

**Interpretation:**
- The standardised coefficient for `sex` is −0.27: a one-standard-deviation change in `sex` leads to a 0.27-standard-deviation change in income
- `iscd11` has the largest effect (β = 0.39)
- The bivariate correlations (`r(y,x)`) show the uncontrolled associations
- The difference between β and r indicates the influence of controlling for other variables

---

### Reliability Analysis – `cronbach()`

Computes Cronbach's Alpha for a scale.

**Example: Reliability of an attitude scale**

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
  n (entfernt): 422
------------------------------------------------------------
Item    M   SD   r(it) Alpha ohne   Empfehlung
pr04 2.20 0.89 -0.1053    -0.1369 ⚠️ entfernen
pr05 1.95 0.83 -0.0987    -0.1591 ⚠️ entfernen
pr07 3.20 0.78 -0.1017    -0.1501 ⚠️ entfernen
============================================================
```

**Interpretation:**
- Cronbach's Alpha = −0.2415 is negative and is rated "unacceptable"
- All item-total correlations are negative, indicating a problem with scale construction
- All items should be removed, as they worsen reliability
- Possible causes: items coded in the wrong direction, or no shared underlying dimension

> **Practical Tip:** Negative Cronbach's Alpha values point to a severe problem with scale construction. Check whether all items are coded in the same direction.

---

## Effect Sizes and Diagnostics

### Computing Effect Sizes – `effect_size()`

Computes common effect size measures and converts between different indices.

**Example 1: Cohen's d from means**

```python
sis.effect_size('cohen_d', m1=3250, m2=3000, sd1=1100, sd2=1050).summary()
```

```
============================================================
  Effektstärke: cohen_d
============================================================
  m1: 3250
  m2: 3000
  sd1: 1100
  sd2: 1050
------------------------------------------------------------
      Maß   Wert Bewertung
Cohen's d 0.2325     klein
r (aus d) 0.1155       ---
============================================================
```

**Interpretation:**
- Cohen's d = 0.23 is classified as a "small" effect
- This corresponds to a correlation of r = 0.12

**Example 2: Converting r to d**

```python
sis.effect_size('r_to_d', r=0.12).summary()
```

```
============================================================
  Effektstärke: r_to_d
============================================================
  r: 0.1200
------------------------------------------------------------
  Maß   Wert  Bewertung
r → d 0.2417 r = 0.1200
============================================================
```

**Example 3: Odds Ratio from a 2×2 table**

```python
sis.effect_size('odds_ratio', a=30, b=10, c=20, d=40).summary()
```

```
============================================================
  Effektstärke: odds_ratio
============================================================
  a: 30
  b: 10
  c: 20
  d: 40
------------------------------------------------------------
      Maß        Wert Bewertung
Odds Ratio        6.00    ---
95%-KI unten      2.25    ---
95%-KI oben      16.00    ---
     ln(OR)       1.79    ---
============================================================
```

**Interpretation:**
- The odds ratio is 6.00, meaning the odds in group A are six times higher than in group B
- The 95% confidence interval [2.25; 16.00] does not include 1, so the difference is statistically significant

---

### Testing for Normality – `normality_test()`

Tests a variable for normality.

```python
sis.normality_test(A18N, 'inc').summary()
```

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
- Both Shapiro-Wilk and Kolmogorov-Smirnov show significant departures from normality
- The distribution is strongly right-skewed (skewness = 2.95)
- Kurtosis is positive (19.01), indicating a more peaked distribution than the normal distribution

> **Practical Tip:** With large samples (n > 500), normality tests are often too sensitive. Focus on graphical inspection and skewness/kurtosis values. A non-normal distribution is typical for income data.

---

### Descriptive Group Comparison – `compare_groups()`

Compares means of several variables across groups.

```python
sis.compare_groups(A18N, 'sex', ['inc', 'age', 'educ']).summary()
```

```
============================================================
  Gruppenvergleich nach sex
============================================================
  Gruppenvariable: sex
  Gruppen: [np.float64(1.0), np.float64(2.0)]
  Variablen: ['inc', 'age', 'educ']
------------------------------------------------------------
Variable M (1.0) SD (1.0)  n (1.0) M (2.0) SD (2.0)  n (2.0)
     inc 2212.97  1519.41     1614 1403.18   887.76     1478
     age   51.42    17.91     1772   51.95    17.36     1700
    educ    3.49     1.26     1771    3.48     1.22     1703
============================================================
```

**Interpretation:**
- Men earn on average more (2,212.97 € vs. 1,403.18 €)
- Women are on average slightly older (51.95 vs. 51.42 years)
- Educational attainment is almost identical (3.49 vs. 3.48)

---

## Exporting Results – `export_results()`

Exports results to various formats.

**Example: Exporting regression results**

```python
result = sis.regress('inc ~ sex + eastwest + iscd11', data=A18N)
sis.export_results(result, 'regression_ergebnis', format='excel')
```

This creates an Excel file `regression_ergebnis.xlsx` with multiple sheets:
- **Statistiken:** The coefficient table
- **Info:** Additional model information

**Supported formats:**

| Format | Description | Use case |
|---|---|---|
| `excel` | Excel file with multiple sheets | Data preparation, presentations |
| `csv` | Separate CSV files per table | Further processing with other tools |
| `html` | HTML file | Web presentations |
| `latex` | LaTeX file | Scientific manuscripts |

> **Practical Tip:** For academic work, the LaTeX format is particularly useful as tables can be inserted directly into the manuscript.

---

## Utility Functions

### `describe_df()`

Prints an overview of all variables in the DataFrame (type, number of valid values, missing values, value range).

### `create_dummies()`

Creates dummy variables from a categorical variable.

### `help_cheatstat()`

Displays integrated help with an overview of all functions and their parameters.

```python
sis.help_cheatstat()
```

---

## Typical Workflows

### Workflow 1: Descriptive Analysis of a Variable

```python
# 1. Check for missing values
sis.missing_report(A18N).summary()

# 2. Create a frequency table
sis.fre(A18N, 'pv19', sort=True).summary()

# 3. With value labels (if available)
sis.fre_wl(A18N, 'pv19', A18L, sort_by_value=True).summary()

# 4. Univariate analysis with statistics
sis.uniV(A18N, 'pv19', se=True).summary()
```

### Workflow 2: Association Analysis

```python
# 1. Create a cross-tabulation
ct = sis.cross_tab(A18N, 'eastwest', 'pv19')
ct.summary(show_tables=True)

# 2. Compute association measures
sis.biV(A18N, 'eastwest', 'pv19', scale='ordinal').summary()

# 3. Compute effect size
result = sis.biV(A18N, 'eastwest', 'pv19', scale='ordinal', notable=True)
d = result['stat'].loc[result['stat']['Maß'] == "Somers' D (Y|X)", 'Wert'].values[0]
sis.effect_size('d_to_r', d=float(d)).summary()
```

### Workflow 3: Regression with Weighting

```python
# 1. Recode variables if necessary
A18N = sis.recode(A18N, 'educ', {'1,2': 1, '3,4': 2, '5': 3}, new_name='educ3')

# 2. Run regression
result = sis.regress('inc ~ sex + eastwest + educ3',
                     data=A18N, weight='wghtpew', robust=True)

# 3. Display results
result.summary()

# 4. Export results
sis.export_results(result, 'regression_inc', format='latex')
```

### Workflow 4: Reliability Analysis of a Scale

```python
# 1. Inspect individual items
sis.uniV(A18N, 'item1').summary()
sis.uniV(A18N, 'item2').summary()
# ... for all items

# 2. Run reliability analysis
cronbach_result = sis.cronbach(A18N, ['pr04', 'pr05', 'pr07'])

# 3. Display results
cronbach_result.summary()

# 4. Create scale variable
A18N = sis.create_index(A18N, ['pr04', 'pr05', 'pr07'],
                        new_name='zufriedenheit')
```

---

## Appendix

### ALLBUS Variable Reference

| Variable | Description | Level of Measurement | Value Range |
|---|---|---|---|
| `sex` | Sex | nominal | 1.0 = male, 2.0 = female |
| `inc` | Income | metric | 25–18,000 € |
| `eastwest` | Region | nominal | 1.0 = East, 2.0 = West |
| `iscd11` | Occupation (ISCED 2011) | ordinal | 1–8 |
| `lm02` | Daily TV viewing time | metric | 1–1,200 minutes |
| `age` | Age | metric | 18–95 years |
| `scage` | Spouse's educational level | ordinal | 1–7 |
| `educ` | Educational attainment | ordinal | 1–7 |
| `pv19` | Probability of voting CDU/CSU | ordinal | 1–10 (Likert) |
| `pr04` | Reunification: more benefits for the West | ordinal | 1–4 |
| `pr05` | Reunification: more benefits for the East | ordinal | 1–4 |
| `pr07` | Citizens in the other part of Germany feel like strangers? | ordinal | 1–4 |
| `wghtpew` | Person weight | metric | 0.54–1.21 |

**Value labels for key variables:**

*educ (educational attainment):*

| Value | Label |
|---|---|
| 1.0 | NO CERTIFICATE |
| 2.0 | LOWEST LEVEL |
| 3.0 | INTERMEDIARY LEVEL |
| 4.0 | QUALI.UNIV.APPL.SCI. |
| 5.0 | QUALI.FOR UNIVERSITY |
| 6.0 | OTHER SCHOOL CERTIF. |
| 7.0 | STILL AT SCHOOL |

*pv19 (probability of voting CDU/CSU):*

| Value | Label |
|---|---|
| 1.0 | VERY UNLIKELY |
| 2.0–9.0 | (intermediate values) |
| 10.0 | VERY LIKELY |

*pr04 / pr05 / pr07:*

| Value | Label |
|---|---|
| 1.0 | COMPLETELY AGREE |
| 2.0 | TEND TO AGREE |
| 3.0 | TEND TO DISAGREE |
| 4.0 | COMPLETELY DISAGREE |

---

### Significance Stars

| Symbol | p-value | Interpretation |
|---|---|---|
| `***` | < 0.001 | highly significant |
| `**` | < 0.01 | significant |
| `*` | < 0.05 | marginally significant |
| `n.s.` | ≥ 0.05 | not significant |

---

### Effect Size Benchmarks

| Measure | Small | Medium | Large |
|---|---|---|---|
| Cohen's d | 0.2 | 0.5 | 0.8 |
| r | 0.1 | 0.3 | 0.5 |
| Eta² | 0.01 | 0.06 | 0.14 |
| Omega² | 0.01 | 0.06 | 0.14 |
| Phi / Cramér's V | 0.1 | 0.3 | 0.5 |

---

### Troubleshooting

**Problem:** `ValueError: Gewichtungsspalte 'wghtpew' nicht gefunden`

> Solution: Check whether the weighting column exists in the DataFrame:
> ```python
> print(A18N.columns)
> ```

**Problem:** `ValueError: Gruppe '3.0' existiert nicht in der Variable 'sex'`

> Solution: Check the available groups:
> ```python
> print(A18N['sex'].unique())
> ```

**Problem:** `LinAlgError: Singular matrix`

> Solution: There is perfect multicollinearity between predictors. Check using `sis.cronbach()` or remove redundant variables.

**Problem:** Cronbach's Alpha is negative

> Solution: Check whether all items are coded in the same direction. Some items may need to be inverted (see `recode()`).

---

## Closing Remarks

cheatstat was developed to make statistical analysis in the social sciences more accessible. It simplifies the most common analysis steps without sacrificing statistical correctness. In particular, native support for weighting in survey data such as the ALLBUS represents a decisive advantage over other Python packages.

> **Important Note:** cheatstat provides simplified weighting suitable for exploratory analyses and teaching purposes. However, it does not account for the full survey design (Primary Sampling Units, Strata) required for correct standard errors and confidence intervals in complex survey data such as the ALLBUS. For scientific publications, please use specialised software such as R with the `survey` package, SAS, or SPSS with the appropriate survey modules.

---

*cheatstat Version 4.1 | Last updated: March 2026 | Author: Jürgen Leibold | License: MIT*