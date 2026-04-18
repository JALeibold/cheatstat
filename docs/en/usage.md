# Basic Usage

[← Installation](installation.md) | [Examples →](examples.md) |
[🇩🇪 Deutsch](../de/usage.md)

---

## Table of Contents

1. [Import and Initialization](#1-import-and-initialization)
2. [The StatResult Object](#2-the-statresult-object)
3. [Loading Data](#3-loading-data)
4. [Weighting in cheatstat](#4-weighting-in-cheatstat)
5. [Missing Values](#5-missing-values)
6. [Accessing Results](#6-accessing-results)
7. [Output and Export](#7-output-and-export)
8. [Tips for Beginners](#8-tips-for-beginners)

---

## 1. Import and Initialization

### Recommended Import

```python
import cheatstat as cs
```

All functions are then available via `cs.function_name()`:

```python
cs.fre(df, 'sex')
cs.uniV(df, 'inc')
cs.biV(df, 'sex', 'educ', scale='nominal')
cs.ttest_u(group='sex', g1=1.0, g2=2.0, dependent='inc', data=df)
cs.regress('inc ~ sex + educ', data=df)
```

### Importing Individual Functions (alternative)

```python
from cheatstat import fre, uniV, biV, ttest_u, regress

fre(df, 'sex')
uniV(df, 'inc')
```

### Show Quick Reference

```python
cs.help_cheatstat()
```

---

## 2. The StatResult Object

Most functions return a `StatResult` object that:
- Contains **tabular results** (as DataFrames)
- Enables **formatted output**
- Provides **dict-like access** to individual results

### Overview

```python
result = cs.uniV(df, 'inc')

# Type of the object
type(result)     # <class 'cheatstat.StatResult'>
repr(result)     # StatResult('Univariate Analyse: inc', 1 Tabellen, mit Statistiken)
```

### `.summary()` – Formatted Output

```python
result.summary()                      # Compact overview
result.summary(show_tables=True)      # Including all tables
```

### `['key']` – Access to Individual Results

```python
result['fre']     # Frequency table as pd.DataFrame
result['stats']   # Statistics as pd.DataFrame
```

### `.keys()` – All Available Keys

```python
result.keys()     # ['stat', 'fre', ...]
```

### `.tables` and `.info` – Direct Attribute Access

```python
result.tables          # dict with all tables
result.info            # dict with metadata (n, variable, ...)
result.test_name       # Name of the analysis
```

### Complete Example

```python
# Generate result
result = cs.ttest_u(group='sex', g1=1.0, g2=2.0,
                    dependent='inc', data=df)

# 1. Formatted output
result.summary()

# 2. Get table as DataFrame
table = result['stat']
print(table)

# 3. Read a single value from the table
t_value = table.loc[table['Statistik'] == 't-Statistik', 'Wert'].values[0]
print(f"t = {t_value}")

# 4. All available keys
print(result.keys())
```

### Filtering Result Tables

```python
result = cs.regress('inc ~ sex + educ', data=df)
table = result['stat']

# Show only significant predictors
significant = table[table['Sig.'].isin(['*', '**', '***'])]
print(significant)
```

---

## 3. Loading Data

### Loading SPSS Files (recommended for ALLBUS)

```python
import pandas as pd

# Numeric values (for analyses)
df_num = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "eastwest", "educ", "pv19", "wghtpew"],
    convert_categoricals=False
)

# Value labels (for frequency tables with labels)
df_lab = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "eastwest", "educ", "pv19", "wghtpew"],
    convert_categoricals=True
)
```

### Loading CSV Files

```python
df = pd.read_csv('data.csv', sep=';', decimal='.')
```

### Loading Excel Files

```python
df = pd.read_excel('data.xlsx', sheet_name='Data')
```

### Loading Stata Files

```python
df = pd.read_stata('data.dta')
```

### Inspecting the Data

```python
# Overview
print(df.shape)           # (n_rows, n_columns)
print(df.dtypes)          # Data types of all columns
print(df.head())          # First 5 rows

# Check missing values
cs.missing_report(df).summary()
```

---

## 4. Weighting in cheatstat

> ⚠️ **IMPORTANT**: cheatstat only provides **simplified weighting**
> for exploratory purposes. For scientific publications, specialized
> survey packages are required.

### How Weighting Works in cheatstat

cheatstat uses:
- **Weighted means**: `Σ(w_i × x_i) / Σ(w_i)`
- **Effective sample size**: `n_eff = (Σw_i)² / Σ(w_i²)` per Korn & Graubard (1999)
- **Rao-Scott correction** for Chi² tests

### Passing Weighting

```python
# As column name (string) – recommended
cs.uniV(df, 'inc', weight='wghtpew').summary()
cs.ttest_u(..., weight='wghtpew', ...)
cs.regress('inc ~ sex', data=df, weight='wghtpew')

# As pd.Series – required for fre() and fre_wl()
cs.fre(df, 'inc', weight=df['wghtpew'])
cs.fre_wl(df, 'inc', dfL, weight=df['wghtpew'])
```

### Effects of Weighting in the ALLBUS

In ALLBUS 2018/2019, there are two weighting values:
- `wghtpew = 0.5448` for East Germans (East German sample is downweighted)
- `wghtpew = 1.2079` for West Germans (West German sample is upweighted)

```python
# Unweighted distribution:
cs.fre(df, 'eastwest')
# → West: 68.65%, East: 31.35%

# Weighted distribution:
cs.fre(df, 'eastwest', weight=df['wghtpew'])
# → reflects the actual population distribution
```

---

## 5. Missing Values

### cheatstat Handles Missing Values Automatically

All functions use **listwise deletion**:
Rows with missing values in the variables used are excluded
for each specific analysis.

```python
# This call is safe even with NaN values in 'inc':
cs.uniV(df, 'inc')    # n (gültig) is reported correctly
cs.ttest_u(group='sex', g1=1.0, g2=2.0, dependent='inc', data=df)
# → uses only cases without NaN in 'sex' and 'inc'
```

### Check Missing Values Before Analysis

```python
cs.missing_report(df).summary()
```

### Handle Missing Values with `recode()`

```python
# Mark values outside valid range as NaN
df = cs.recode(df, 'inc', {
    '>0 and <=20000': 'valid',
    'else': np.nan
}, new_name='inc_clean')
```

---

## 6. Accessing Results

### Universal Access Pattern

```python
# Step 1: Generate result
result = cs.regress('inc ~ sex + educ', data=df)

# Step 2: Show available keys
print(result.keys())
# → ['stat', 'model', 'anova', 'Formel', 'Methode', ...]

# Step 3: Get desired table
coefficients = result['stat']
print(coefficients)

# Step 4: Export as Excel
cs.export_results(result, 'my_regression')
```

### Available Keys per Function

| Function | Available Keys |
|----------|---------------|
| `uniV()` | `'fre'`, `'stats'` |
| `cross_tab()` | `'observed'`, `'col_percent'`, `'row_percent'`, `'total_percent'`, `'expected'`, `'residuals'`, `'st_residuals'`, `'deff'`, `'p_value_deff'` |
| `biV()` | `'stat'`, `'cross_tab'` |
| `ttest_u()` | `'stat'` |
| `regress()` | `'stat'`, `'model'`, `'anova'` |
| `beta()` (full=True) | `'stat'` |
| `cronbach()` | `'stat'` |
| `effect_size()` | `'stat'` |
| `normality_test()` | `'stat'` |
| `compare_groups()` | `'stat'` |
| `missing_report()` | `'stat'` |

---

## 7. Output and Export

### Display in Jupyter Notebook

```python
# Direct display as formatted table
result = cs.uniV(df, 'inc')
result['stats']          # Automatically displayed as formatted table
```

### Process Table as DataFrame

```python
result = cs.regress('inc ~ sex + educ', data=df)
table = result['stat']

# Save as CSV
table.to_csv('regression.csv', sep=';', decimal='.', index=False)

# Save as Excel
table.to_excel('regression.xlsx', index=False)
```

### Export with `export_results()`

```python
result = cs.regress('inc ~ sex + educ', data=df)

# Excel (default)
cs.export_results(result, 'regression_result')

# CSV
cs.export_results(result, 'regression_result', format='csv')

# LaTeX for academic papers
cs.export_results(result, 'regression_result', format='latex')

# HTML for web reports
cs.export_results(result, 'regression_result', format='html')
```

---

## 8. Tips for Beginners

### Tip 1: Always Start with `missing_report()`

```python
cs.missing_report(df).summary()
```

### Tip 2: Use `.summary()` for a Quick Overview

```python
cs.uniV(df, 'inc').summary()
cs.biV(df, 'sex', 'inc', 'ordinal').summary()
cs.regress('inc ~ sex + educ', data=df).summary()
```

### Tip 3: Use `notable=True` for Quick Statistics

```python
# Only association measures, no cross-table
cs.biV(df, 'eastwest', 'pv19', scale='ordinal', notable=True).summary()
```

### Tip 4: Know Your Variable Types

```python
# Check data types
print(df['sex'].dtype)        # float64 → numeric
print(df['educ'].dtype)       # float64 → numeric

# Show unique values
print(df['sex'].unique())     # [1.0, 2.0]
print(df['educ'].unique())    # [1.0, 2.0, 3.0, ...]
```

### Tip 5: Specify the Scale Level Correctly

| Scale level | `scale=` parameter | Output |
|-------------|-------------------|--------|
| Nominal (categories) | `'nominal'` or `'n'` | Chi², G², Phi/Cramér's V |
| Ordinal or metric | `'ordinal'` or `'om'` | Pearson-r, Spearman-ρ, Kendall-τ, Somers' D |

### Tip 6: Check Group Names

```python
# Check group values before t-test
print(df['sex'].unique())    # [1.0, 2.0, nan]
# → g1=1.0, g2=2.0 (as float, not as string!)

cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=df).summary()
```

### Tip 7: Two DataFrames for Labels

```python
# df_num: numeric values for analyses
# df_lab: labels for frequency tables

cs.fre_wl(df_num, 'educ', df_lab)
```

---

*cheatstat Version 4.1 | Author: Jürgen Leibold | March 2026*

[→ Next: Examples](examples.md) |
[← Installation](installation.md) |
[← Back to Overview](index.md)

