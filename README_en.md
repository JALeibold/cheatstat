<div align="center">

# cheatstat

**Simple Statistical Functions for Social Scientists**

[![PyPI version](https://img.shields.io/pypi/v/cheatstat?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/cheatstat/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![statsmodels](https://img.shields.io/badge/statsmodels-optional-green)](https://www.statsmodels.org)
[![Documentation](https://img.shields.io/badge/Documentation-English-blue?logo=github)](docs/en/index.md)

[🇩🇪 Deutsche Dokumentation](README_de.md)

</div>

---

## ⚠️ Important Note on Weighting

> This implementation is an **approximation**. For scientific publications,
> the complete survey design (PSU, Strata) must be considered.

cheatstat provides simplified weighting suitable for **exploratory analyses
and teaching purposes**. It does **not** account for the complete survey design
(Primary Sampling Units, Strata).

| cheatstat is **not** for | cheatstat is **ideal** for |
|--------------------------|------------------------------|
| Official statistical reports | Social science courses |
| Scientific publications | Exploratory data analysis |
| Political decision-making | Quick hypothesis testing |
| | Introduction to statistical methods |

**For scientific publications, please use:**
`survey` (R) · `SURVEYMEANS` (SAS) · *Complex Samples* (SPSS)

---

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Function Overview](#function-overview)
- [ALLBUS Examples](#allbus-examples)
- [Accessing Results](#accessing-results)
- [Documentation](#documentation)
- [Dependencies](#dependencies)
- [License](#license)

---

## Installation

```bash
# Basic installation
pip install cheatstat

# Recommended: with OLS regression
pip install cheatstat statsmodels

# Full: with all optional packages
pip install cheatstat statsmodels numba openpyxl pyreadstat
```

---

## Getting Started

```python
import cheatstat as cs
import pandas as pd

# Load ALLBUS data
A18N = pd.read_spss('ALLBUS2018.sav',
    usecols=["sex", "inc", "eastwest", "iscd11", "pv19", "wghtpew"],
    convert_categoricals=False)

A18L = pd.read_spss('ALLBUS2018.sav',
    usecols=["sex", "inc", "eastwest", "iscd11", "pv19", "wghtpew"],
    convert_categoricals=True)

# Show quick reference
cs.help_cheatstat()
```

---

## Function Overview

| Function | Description |
|----------|-------------|
| `missing_report(df)` | Missing value analysis |
| `recode(df, col, mapping)` | Recode variables |
| `fre(df, col)` | Frequency table |
| `fre_wl(df, col, labels)` | Frequency table with value labels |
| `uniV(df, col)` | Univariate analysis |
| `cross_tab(df, col1, col2)` | Cross-tabulation |
| `biV(df, col1, col2, scale)` | Bivariate analysis |
| `ttest_u(group, g1, g2, dependent, data)` | Independent samples t-test |
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

## ALLBUS Examples

### Missing Value Analysis

```python
cs.missing_report(A18N).summary()
```

```
  Variable  n (valid)  n (missing)  % missing Status
     scage       1916         1561      44.90      🔴
    isco08       1950         1527      43.92      🔴
       inc       3092          385      11.07      🔴
  eastwest       3477            0       0.00      ✅
       sex       3477            0       0.00      ✅
```

---

### Frequency Table with Labels

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

### Univariate Analysis

```python
cs.uniV(A18N, 'inc').summary()
```

```
  50th percentile (Median)    1500.00
              Mean          1825.8865
    Standard deviation      1320.9836
              Skewness         2.9523
```

---

### Association Measures (biV)

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
   t-statistic   18.274488
       p-value   0.00e+00   ***
 Difference      €809.79
     Cohen's d   0.6439 (medium)
```

```python
# With survey weighting
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N, weight='wghtpew').summary()
```

```
 Difference       €891.93
     Cohen's d    0.6928 (medium-large)
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
# With weighting and robust SE
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N,
           weight='wghtpew', robust=True).summary()
```

---

### Reliability Analysis

```python
cs.cronbach(A18N, ['pr04', 'pr05', 'pr07']).summary()
```

```
  Cronbach's Alpha: -0.2415
  Rating: unacceptable
```

---

### Effect Sizes

```python
cs.effect_size('cohen_d', m1=2213, m2=1403, sd1=1519, sd2=888).summary()
# → Cohen's d = 0.6439 (medium)

cs.effect_size('r_to_d', r=0.10).summary()
# → d = 0.2010

cs.effect_size('odds_ratio', a=30, b=10, c=20, d=40).summary()
# → OR = 6.00, 95% CI [2.25, 16.00]
```

---

### Recoding Variables

```python
# Education categories
A18N = cs.recode(A18N, 'educ',
    {'1,2': 1, '3,4': 2, '5': 3}, new_name='educ3')

# Age categories
A18N = cs.recode(A18N, 'age',
    {'18-34': 1, '35-54': 2, '55-99': 3}, new_name='age3')

# Complex conditions
A18N = cs.recode(A18N, 'inc',
    {'<1000': 1, '>=1000 and <2500': 2, '>=2500': 3}, new_name='inc3')
```

---

### Export

```python
result = cs.regress('inc ~ sex + eastwest + iscd11', data=A18N)

# Excel (default)
cs.export_results(result, 'regression_result')

# LaTeX for academic papers
cs.export_results(result, 'regression_result', format='latex')
```

---

## Accessing Results

All functions return a `StatResult` object:

```python
result = cs.regress('inc ~ sex + eastwest + iscd11', data=A18N)

result.summary()                   # Formatted output
result.summary(show_tables=True)   # Including all tables
result['stat']                     # Coefficients as DataFrame
result['model']                    # statsmodels object
result['model'].summary()          # Original statsmodels output
result.keys()                      # All available keys
```

| Key | Content |
|-----|---------|
| `'stat'` | Main results table |
| `'fre'` | Frequency table (uniV) |
| `'observed'` | Observed frequencies (cross_tab) |
| `'col_percent'` | Column percentages (cross_tab) |
| `'model'` | statsmodels object (regress) |
| `'anova'` | ANOVA table (regress) |
| `'cross_tab'` | Cross-tabulation (biV) |

---

## Documentation

| Language | Content |
|----------|---------|
| [📖 Main Documentation (EN)](docs/en/index.md) | Complete guide |
| [📦 Installation (EN)](docs/en/installation.md) | pip, conda, dependencies |
| [🚀 Basic Usage (EN)](docs/en/usage.md) | StatResult, tips |
| [💡 Examples (EN)](docs/en/examples.md) | ALLBUS examples with output |
| [📋 API Reference (EN)](docs/en/api.md) | All parameters and returns |

---

## Dependencies

### Required (automatically installed)

| Package | Usage |
|---------|-------|
| `pandas ≥ 1.3` | Data processing |
| `numpy ≥ 1.20` | Numerical calculations |
| `scipy ≥ 1.7` | Statistical tests |

### Optional (recommended)

| Package | For | Installation |
|---------|-----|-------------|
| `statsmodels` | `regress()` | `pip install statsmodels` |
| `numba` | Faster calculations | `pip install numba` |
| `openpyxl` | Excel export | `pip install openpyxl` |
| `pyreadstat` | Loading SPSS files | `pip install pyreadstat` |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

*cheatstat Version 4.1 | Author: Jürgen Leibold | March 2026*

[⬆️ Back to top](#cheatstat) | [🇩🇪 Deutsche Dokumentation](README_de.md)

</div>

