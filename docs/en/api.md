# API Reference

[← Examples](examples.md) | [🇩🇪 Deutsch](../de/api.md) |
[← Back to Overview](index.md)

---

## Table of Contents

- [StatResult](#statresult)
- [missing_report](#missing_report)
- [recode](#recode)
- [fre](#fre)
- [fre_wl](#fre_wl)
- [uniV](#univ)
- [cross_tab](#cross_tab)
- [biV](#biv)
- [ttest_u](#ttest_u)
- [regress](#regress)
- [beta](#beta)
- [cronbach](#cronbach)
- [effect_size](#effect_size)
- [normality_test](#normality_test)
- [compare_groups](#compare_groups)
- [export_results](#export_results)
- [create_dummies](#create_dummies)
- [help_cheatstat](#help_cheatstat)

---

## StatResult

```
StatResult(tables=None, stat=None, test_name="", info=None)
```

Unified container for all analysis results in cheatstat.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `tables` | dict | Named DataFrames (e.g. `{'observed': df, ...}`) |
| `stat` | pd.DataFrame | Main results table (statistics, coefficients) |
| `test_name` | str | Name of the analysis |
| `info` | dict | Metadata (n, formula, method, ...) |

### Methods

#### `.summary(show_tables=False)`

Prints a formatted summary to the console.

```python
result.summary()                  # Statistics only
result.summary(show_tables=True)  # Including all tables
```

#### `['key']`

Dict-like access to results.

```python
result['stat']          # Statistics DataFrame
result['observed']      # Table by name
result['R²']            # Info value
```

#### `.keys()`

Returns all available keys.

```python
result.keys()    # ['stat', 'observed', 'col_percent', ...]
```

---

## missing_report

```
missing_report(df, threshold=5.0)
```

Creates a report on missing values for all columns.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `threshold` | float | 5.0 | Warning threshold in percent |

### Returns

`StatResult` with:
- `result['stat']`: Table with variable, n (valid), n (missing), % missing, status
- `result.info`: Summary (total, complete, with missing, ...)

### Example

```python
cs.missing_report(A18N).summary()
cs.missing_report(A18N, threshold=10.0).summary()
```

---

## recode

```
recode(df, column, mapping, new_name=None, else_value=np.nan)
```

Recodes a variable according to a mapping table.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `column` | str | – | Source column name |
| `mapping` | dict | – | Mapping {condition: value} |
| `new_name` | str | None | Target column name (None = overwrite) |
| `else_value` | any | np.nan | Value for unassigned cases |

### Mapping Formats

| Format | Example | Meaning |
|--------|---------|---------|
| Comma-separated | `'1,2,4'` | Exactly these values |
| Range | `'1-6'` | Values from 1 to 6 |
| Greater than | `'>5'` | Values > 5 |
| Less than or equal | `'<=3'` | Values ≤ 3 |
| AND | `'>=2 and <=6'` | Values between 2 and 6 |
| OR | `'<2 or >8'` | Values < 2 or > 8 |
| NOT | `'not 5'` | All except 5 |
| ELSE | `'else'` | All remaining |
| Tuple | `(1, 6)` | Range 1–6 |
| Number | `5` | Exact value 5 |

### Returns

`pd.DataFrame` with new/overwritten column.

### Examples

```python
# Simple
df = cs.recode(df, 'educ', {'1,2': 1, '3,4': 2, '5': 3},
               new_name='educ3')

# Range
df = cs.recode(df, 'age', {'18-29': 1, '30-49': 2, '50-99': 3},
               new_name='age3')

# Complex
df = cs.recode(df, 'inc', {'<1000': 1, '>=1000 and <3000': 2, '>=3000': 3},
               new_name='inc3')

# Reverse scale
df = cs.recode(df, 'item1', {1: 5, 2: 4, 3: 3, 4: 2, 5: 1},
               new_name='item1_r')
```

---

## fre

```
fre(df, column, weight=None, sort=True, round_digits=2)
```

Creates a frequency table for a variable.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `column` | str | – | Column name |
| `weight` | str/pd.Series | None | Weighting (column name or pd.Series) |
| `sort` | bool | True | Sort by value ascending |
| `round_digits` | int | 2 | Decimal places for percentages |

### Returns

`pd.DataFrame` with columns:
- `Ausprägung`: Categories
- `Häufigkeiten`: Absolute frequencies
- `Prozent`: Percentage (incl. missing)
- `kum. Prozente`: Cumulative percentage
- `gültigeP`: Valid percentage (excl. missing)
- `kum.gültigeP`: Cumulative valid percentage

### Examples

```python
cs.fre(A18N, 'sex', sort=True, round_digits=2)
cs.fre(A18N, 'sex', weight='wghtpew')
cs.fre(A18N, 'pv19', sort=True, round_digits=1)
```

> **Note:** `weight` can now be either a column name (str) or a pd.Series.

---

## fre_wl

```
fre_wl(df, column, labels, weight=None, sort_by_value=True, round_digits=2)
```

Creates a frequency table with value labels.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `column` | str | – | Column name |
| `labels` | pd.DataFrame/pd.Series | – | Value labels |
| `weight` | str/pd.Series | None | Weighting (column name or pd.Series) |
| `sort_by_value` | bool | True | Sort by value |
| `round_digits` | int | 2 | Decimal places |

### Returns

`pd.DataFrame` with columns:
- `Ausprägung`: Numeric value
- `Label`: Value label
- `Häufigkeiten`, `Prozent`, `kum. Prozente`, `gültigeP`, `kum.gültigeP`

### Example

```python
cs.fre_wl(A18N, 'educ', A18L)
cs.fre_wl(A18N, 'pv19', A18L['pv19'], weight='wghtpew')
```

---

## uniV

```
uniV(df, column_name, weight=None, se=False)
```

Univariate analysis: frequency table + descriptive statistics.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `column_name` | str | – | Column name |
| `weight` | str/pd.Series | None | Weighting |
| `se` | bool | False | Show standard errors |

### Returns

`StatResult` with:
- `result['fre']`: Frequency table (pd.DataFrame)
- `result['stats']` / `result['stat']`: Descriptive statistics (pd.DataFrame)
- `result.info`: n (total), n (valid), n (effective with weighting)

### Descriptive Statistics

| Statistic | Description |
|-----------|-------------|
| Mode | Most frequent value |
| 25th percentile | First quartile |
| 50th percentile (Median) | Central value |
| 75th percentile | Third quartile |
| IQR | Interquartile range |
| Mean | Arithmetic mean |
| 95% CI (lower/upper) | Confidence interval of the mean |
| Minimum / Maximum | Extreme values |
| Variance | Measure of dispersion |
| Standard deviation | Measure of dispersion |
| Skewness | Asymmetry of the distribution |
| Kurtosis | Peakedness of the distribution |
| Excess | Kurtosis − 3 |

### Examples

```python
cs.uniV(A18N, 'inc').summary()
cs.uniV(A18N, 'inc', weight='wghtpew').summary()
cs.uniV(A18N, 'inc', se=True).summary()

# Access tables
result = cs.uniV(A18N, 'inc')
result['fre']     # Frequency table
result['stats']   # Statistics
```

---

## cross_tab

```
cross_tab(df, col1, col2, weight=None, round_digits=2,
          show_expected=True, show_residuals=True,
          show_deff=True, show_deff_p=True)
```

Creates a weighted cross-tabulation.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `col1` | str | – | Row variable |
| `col2` | str | – | Column variable |
| `weight` | str/pd.Series | None | Weighting |
| `round_digits` | int | 2 | Decimal places |
| `show_expected` | bool | True | Show expected frequencies |
| `show_residuals` | bool | True | Show standardized residuals |
| `show_deff` | bool | True | Show design effect |
| `show_deff_p` | bool | True | Show corrected p-value |

### Returns

`StatResult` with:
- `result['observed']`: Observed frequencies
- `result['col_percent']`: Column percentages
- `result['row_percent']`: Row percentages
- `result['total_percent']`: Total percentages
- `result['expected']`: Expected frequencies
- `result['residuals']`: Simple residuals
- `result['st_residuals']`: Standardized residuals
- `result['deff']`: Design effect (only with weighting)
- `result['p_value_deff']`: Corrected p-value (only with weighting)

### Examples

```python
ct = cs.cross_tab(A18N, 'sex', 'eastwest')
ct.summary(show_tables=True)
ct['observed']         # Observed frequencies
ct['col_percent']      # Column percentages

# Without design effect
ct = cs.cross_tab(A18N, 'sex', 'educ',
                  show_deff=False, show_deff_p=False)
```

---

## biV

```
biV(df, col1, col2, scale, weight=None, round_digits=2, notable=False)
```

Bivariate analysis with association measures.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `col1` | str | – | First variable |
| `col2` | str | – | Second variable |
| `scale` | str | – | Scale level (see below) |
| `weight` | str/pd.Series | None | Weighting |
| `round_digits` | int | 2 | Decimal places |
| `notable` | bool | False | Statistics only, no cross-table |

### Scale Parameter

| `scale=` | Accepted values | Calculated measures |
|----------|----------------|---------------------|
| Nominal | `'nominal'`, `'n'`, `'kategorial'`, `'kat'` | Chi², G², Phi (2×2) / Cramér's V |
| Ordinal/metric | `'ordinal'`, `'om'`, `'metrisch'`, `'ordinal-metrisch'` | Pearson-r, Spearman-ρ, Kendall-τ, Somers' D |

### Returns

`StatResult` with:
- `result['stat']`: Association measures with p-values and significance stars
- `result['cross_tab']`: Cross-tabulation (StatResult, if `notable=False`)

### Examples

```python
# Nominal
cs.biV(A18N, 'sex', 'eastwest', scale='nominal').summary()

# Ordinal
cs.biV(A18N, 'eastwest', 'pv19', scale='ordinal').summary()

# Statistics only
cs.biV(A18N, 'sex', 'educ', scale='nominal', notable=True).summary()

# With weighting
cs.biV(A18N, 'eastwest', 'pv19', scale='ordinal',
       weight='wghtpew').summary()
```

---

## ttest_u

```
ttest_u(group, g1, g2, dependent, data=None, weight=None,
        levene_test='median', autoLevene=True)
```

Independent samples t-test for two groups.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `group` | str | – | Grouping variable name |
| `g1` | int/float/str | – | First group value |
| `g2` | int/float/str | – | Second group value |
| `dependent` | str | – | Dependent variable |
| `data` | pd.DataFrame | None | Input data (**required**) |
| `weight` | str/pd.Series | None | Weighting |
| `levene_test` | str | `'median'` | Levene test type: `'mean'`, `'median'`, `'trimmed'` |
| `autoLevene` | bool | True | Automatic test selection via Levene |

### Returns

`StatResult` with `result['stat']`:

| Statistic | Description |
|-----------|-------------|
| Test | Test used (Student-t / Welch-t) |
| t-Statistik | t-value |
| p-Wert | Significance |
| df | Degrees of freedom (Welch-Satterthwaite) |
| Mittelwert G1/G2 | Group means |
| Differenz (G1-G2) | Mean difference |
| 95%-KI unten/oben | Confidence interval of the difference |
| Varianz G1/G2 | Group variances |
| Cohen's d | Effect size |
| n G1/G2 (roh/eff) | Sample sizes |
| Levene p | p-value of the Levene test |

### Decision Logic

- `autoLevene=True` (default): Levene test decides automatically
  → p(Levene) > 0.05: Student-t | p(Levene) ≤ 0.05: Welch-t
- `autoLevene=False`: Always Welch-t (recommended with weighting)
- With weighting: Levene test is not performed, Welch-t is used

### Examples

```python
# Standard
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N).summary()

# With weighting
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N, weight='wghtpew').summary()

# Without automatic selection
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N, autoLevene=False).summary()
```

---

## regress

```
regress(formula, data, weight=None, robust=False,
        show_beta=True, show_ci=True, show_vif=True)
```

OLS regression with standardized coefficients, VIF and 95% CI.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `formula` | str | – | R-formula: `'y ~ x1 + x2 + ...'` |
| `data` | pd.DataFrame | – | Input data |
| `weight` | str | None | Weighting column → WLS |
| `robust` | bool | False | Robust standard errors HC3 (default: False) |
| `show_beta` | bool | True | Show standardized β (default: True) |
| `show_ci` | bool | True | 95% CI (default: True) |
| `show_vif` | bool | True | VIF (default: True) |

### Formula Syntax

| Syntax | Meaning |
|--------|---------|
| `'y ~ x1 + x2'` | Simple regression |
| `'y ~ C(x1) + x2'` | x1 as categorical variable |
| `'y ~ x1 + x2 + x1:x2'` | With interaction term |

### Returns

`StatResult` with:
- `result['stat']`: Coefficient table
- `result['model']`: statsmodels `RegressionResults` object
- `result['anova']`: ANOVA table Type 2
- `result.summary()`: Formatted output
- `result['model'].summary()`: Original statsmodels output

### Coefficient Table

| Column | Description |
|--------|-------------|
| `Variable` | Predictor name |
| `b` | Unstandardized coefficient |
| `SE` | Standard error |
| `Beta (β)` | Standardized coefficient |
| `t` | t-value |
| `p-Wert` | Significance |
| `Sig.` | Stars (***/**/*/ n.s.) |
| `95%-KI unten/oben` | Confidence interval |
| `VIF` | Variance Inflation Factor |

### VIF Interpretation

| VIF | Meaning |
|-----|---------|
| < 5 | No problem |
| 5–10 | Moderate multicollinearity ⚠️ |
| > 10 | Strong multicollinearity 🔴 |

### Examples

```python
# Standard OLS
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N).summary()

# WLS with weighting
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N,
           weight='wghtpew').summary()

# Robust standard errors
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N,
           robust=True).summary()

# Categorical variable
cs.regress('inc ~ sex + eastwest + C(iscd11)', data=A18N).summary()

# Further processing
result = cs.regress('inc ~ sex + educ', data=A18N)
result['model'].resid          # Residuals
result['model'].fittedvalues   # Predicted values
result['anova']                # ANOVA table
```

---

## beta

```
beta(formula, data, weight=None, full=False)
```

Calculates standardized regression coefficients (β).

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `formula` | str | – | R-formula: `'y ~ x1 + x2 + ...'` |
| `data` | pd.DataFrame | – | Input data |
| `weight` | str/pd.Series | None | Weighting |
| `full` | bool | False | Complete table with SE, t, p |

### Returns

- `full=False`: `pd.Series` with β coefficients (incl. R², n as attributes)
- `full=True`: `StatResult` with complete regression table

### Examples

```python
# Simple: only β
b = cs.beta('inc ~ sex + eastwest + iscd11', data=A18N)
print(b)
print(f"R² = {b.attrs['R_squared']:.4f}")

# Complete: with SE, t, p
cs.beta('inc ~ sex + eastwest + iscd11', data=A18N, full=True).summary()

# With weighting
cs.beta('inc ~ sex + eastwest + iscd11', data=A18N,
        weight='wghtpew', full=True).summary()
```

---

## cronbach

```
cronbach(df, items, weight=None, item_analysis=True)
```

Calculates Cronbach's Alpha and item analysis.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `items` | list | – | Item column names |
| `weight` | str/pd.Series | None | Weighting (currently unweighted) |
| `item_analysis` | bool | True | Calculate item-total correlations |

### Returns

`StatResult` with:
- `result['stat']`: Item analysis table (M, SD, r(it), Alpha without Item, Recommendation)
- `result.info`: Alpha, Rating, k Items, n (Listwise)

### Alpha Rating

| Alpha | Rating |
|-------|--------|
| ≥ 0.90 | Excellent |
| ≥ 0.80 | Good |
| ≥ 0.70 | Acceptable |
| ≥ 0.60 | Questionable |
| ≥ 0.50 | Poor |
| < 0.50 | Unacceptable |

### Example

```python
cs.cronbach(A18N, ['pr04', 'pr05', 'pr07']).summary()
cs.cronbach(A18N, ['item1', 'item2', 'item3', 'item4'],
            item_analysis=False).summary()
```

---

## effect_size

```
effect_size(test_type, **kwargs)
```

Calculates common effect sizes.

### Parameters

| `test_type` | Required parameters | Optional parameters |
|-------------|---------------------|---------------------|
| `'cohen_d'` | `m1, m2, sd1, sd2` | `n1, n2` |
| `'eta_sq'` | `f, df1, df2` | – |
| `'omega_sq'` | `f, df1, df2` | `n` |
| `'r_to_d'` | `r` | – |
| `'d_to_r'` | `d` | – |
| `'odds_ratio'` | `a, b, c, d` | – |

### Effect Size Rating

| Measure | Small | Medium | Large |
|---------|-------|--------|-------|
| Cohen's d | 0.20 | 0.50 | 0.80 |
| r | 0.10 | 0.30 | 0.50 |
| Eta² | 0.01 | 0.06 | 0.14 |

### Examples

```python
cs.effect_size('cohen_d', m1=2213, m2=1403, sd1=1519, sd2=888).summary()
cs.effect_size('eta_sq', f=4.5, df1=2, df2=97).summary()
cs.effect_size('r_to_d', r=0.12).summary()
cs.effect_size('d_to_r', d=0.64).summary()
cs.effect_size('odds_ratio', a=30, b=10, c=20, d=40).summary()
```

---

## normality_test

```
normality_test(df, column)
```

Tests a variable for normal distribution.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `column` | str | – | Column name |

### Returns

`StatResult` with tests:
- Shapiro-Wilk (only for n < 5,000)
- Kolmogorov-Smirnov
- Skewness (z-standardized)
- Kurtosis (z-standardized)

### Example

```python
cs.normality_test(A18N, 'inc').summary()
cs.normality_test(A18N, 'pv19').summary()
```

---

## compare_groups

```
compare_groups(df, group, variables, weight=None)
```

Compares means of multiple variables across groups.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `group` | str | – | Grouping variable |
| `variables` | list | – | Variables to compare |
| `weight` | str/pd.Series | None | Weighting |

### Returns

`StatResult` with table: Mean, SD, n for each group and variable.

### Example

```python
cs.compare_groups(A18N, 'sex', ['inc', 'age', 'educ']).summary()
cs.compare_groups(A18N, 'eastwest', ['inc', 'pv19'],
                  weight='wghtpew').summary()
```

---

## export_results

```
export_results(result, filename, format='excel', decimal=',')
```

Exports analysis results to a file.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `result` | StatResult/pd.DataFrame | – | Results to export |
| `filename` | str | – | Filename **without** extension |
| `format` | str | `'excel'` | Format: `'excel'`, `'csv'`, `'html'`, `'latex'` |
| `decimal` | str | `','` | Decimal separator (CSV only) |

### Export Formats

| Format | File | Application |
|--------|------|-------------|
| `'excel'` | `.xlsx` | Excel, LibreOffice Calc |
| `'csv'` | `.csv` | R, SPSS, spreadsheet software |
| `'html'` | `.html` | Web reports |
| `'latex'` | `.tex` | Scientific papers |

### Examples

```python
result = cs.regress('inc ~ sex + educ', data=A18N)
cs.export_results(result, 'regression')
cs.export_results(result, 'regression', format='latex')
cs.export_results(result, 'regression', format='csv', decimal=',')
```

---

## create_dummies

```
create_dummies(df, column, prefix=None)
```

Creates dummy variables and appends them to the DataFrame.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | pd.DataFrame | – | Input data |
| `column` | str | – | Source column (must be numeric) |
| `prefix` | str | None | Prefix for dummy columns (default: column name) |

### Returns

`pd.DataFrame` with appended dummy columns.
Decimal places are removed (e.g. `educ_3` instead of `educ_3.0`).

### Examples

```python
A18N = cs.create_dummies(A18N, 'educ', prefix='educ')
# → New columns: educ_1, educ_2, educ_3, educ_4, educ_5, educ_6, educ_7

A18N = cs.create_dummies(A18N, 'eastwest')
# → New columns: eastwest_1, eastwest_2
```

---

## help_cheatstat

```
help_cheatstat()
```

Prints a compact quick reference of all functions to the console.

```python
cs.help_cheatstat()
```

---

*cheatstat Version 4.1.2 | Author: Jürgen Leibold | March 2026*

[← Examples](examples.md) | [← Back to Overview](index.md)
