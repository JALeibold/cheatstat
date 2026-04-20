# Grundlegende Nutzung

[← Installation](installation.md) | [Beispiele →](examples.md) |
[🇬🇧 English](../en/usage.md)

---

## Inhaltsverzeichnis

1. [Import und Initialisierung](#1-import-und-initialisierung)
2. [Das StatResult-Objekt](#2-das-statresult-objekt)
3. [Daten laden](#3-daten-laden)
4. [Gewichtung in cheatstat](#4-gewichtung-in-cheatstat)
5. [Fehlende Werte](#5-fehlende-werte)
6. [Ergebnisse abrufen](#6-ergebnisse-abrufen)
7. [Ausgabe und Export](#7-ausgabe-und-export)
8. [Tipps für Einsteiger](#8-tipps-für-einsteiger)

---

## 1. Import und Initialisierung

### Empfohlener Import

```python
import cheatstat as cs
```

Alle Funktionen sind dann über `cs.funktionsname()` verfügbar:

```python
cs.fre(df, 'sex')
cs.uniV(df, 'inc')
cs.biV(df, 'sex', 'educ', scale='nominal')
cs.ttest_u(group='sex', g1=1.0, g2=2.0, dependent='inc', data=df)
cs.regress('inc ~ sex + educ', data=df)
```

### Einzelne Funktionen importieren (alternative Methode)

```python
from cheatstat import fre, uniV, biV, ttest_u, regress

fre(df, 'sex')
uniV(df, 'inc')
```

### Kurzanleitung anzeigen

```python
cs.help_cheatstat()
```

---

## 2. Das StatResult-Objekt

Die meisten Funktionen geben ein `StatResult`-Objekt zurück, das:
- **Tabellarische Ergebnisse** enthält (als DataFrames)
- **Formatierte Ausgabe** ermöglicht
- **Dict-ähnlichen Zugriff** auf einzelne Ergebnisse bietet

### Überblick

```python
result = cs.uniV(df, 'inc')

# Art des Objekts
type(result)     # <class 'cheatstat.StatResult'>
repr(result)     # StatResult('Univariate Analyse: inc', 1 Tabellen, mit Statistiken)
```

### `.summary()` – Formatierte Ausgabe

```python
result.summary()                      # Kompakte Übersicht
result.summary(show_tables=True)      # Inkl. aller Tabellen
```

### `['schlüssel']` – Zugriff auf einzelne Ergebnisse

```python
result['fre']     # Häufigkeitstabelle als pd.DataFrame
result['stats']   # Statistiken als pd.DataFrame
```

### `.keys()` – Alle verfügbaren Schlüssel

```python
result.keys()     # ['stat', 'fre', ...]
```

### `.tables` und `.info` – Direkter Attributzugriff

```python
result.tables          # dict mit allen Tabellen
result.info            # dict mit Metadaten (n, Variable, ...)
result.test_name       # Name der Analyse
```

### Vollständiges Beispiel

```python
# Ergebnis erzeugen
result = cs.ttest_u(group='sex', g1=1.0, g2=2.0,
                    dependent='inc', data=df)

# 1. Formatierte Ausgabe
result.summary()

# 2. Tabelle als DataFrame abrufen
tabelle = result['stat']
print(tabelle)

# 3. Einzelnen Wert aus der Tabelle lesen
t_wert = tabelle.loc[tabelle['Statistik'] == 't-Statistik', 'Wert'].values[0]
print(f"t = {t_wert}")

# 4. Alle verfügbaren Schlüssel
print(result.keys())
```

### Ergebnistabelle filtern

```python
result = cs.regress('inc ~ sex + educ', data=df)
tabelle = result['stat']

# Nur signifikante Prädiktoren anzeigen
signifikant = tabelle[tabelle['Sig.'].isin(['*', '**', '***'])]
print(signifikant)
```

---

## 3. Daten laden

### SPSS-Datei laden (empfohlen für ALLBUS)

```python
import pandas as pd

# Numerische Werte (für Analysen)
df_num = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "eastwest", "educ", "pv19", "wghtpew"],
    convert_categoricals=False
)

# Wertelabels (für Häufigkeitstabellen mit Labels)
df_lab = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "eastwest", "educ", "pv19", "wghtpew"],
    convert_categoricals=True
)
```

### CSV-Datei laden

```python
df = pd.read_csv('daten.csv', sep=';', decimal=',')
```

### Excel-Datei laden

```python
df = pd.read_excel('daten.xlsx', sheet_name='Daten')
```

### Stata-Datei laden

```python
df = pd.read_stata('daten.dta')
```

### Daten prüfen

```python
# Überblick
print(df.shape)           # (n_zeilen, n_spalten)
print(df.dtypes)          # Datentypen aller Spalten
print(df.head())          # Erste 5 Zeilen

# Fehlende Werte prüfen
cs.missing_report(df).summary()
```

---

## 4. Gewichtung in cheatstat

> ⚠️ **WICHTIG**: cheatstat bietet nur eine **vereinfachte Gewichtung**
> für explorative Zwecke. Für wissenschaftliche Publikationen sind
> spezialisierte Survey-Pakete erforderlich.

### Wie Gewichtung in cheatstat funktioniert

cheatstat verwendet:
- **Gewichtete Mittelwerte**: `Σ(w_i × x_i) / Σ(w_i)`
- **Effektive Stichprobengröße**: `n_eff = (Σw_i)² / Σ(w_i²)` nach Korn & Graubard (1999)
- **Rao-Scott-Korrektur** für Chi²-Tests

### Gewichtung übergeben

```python
# Als Spaltenname (String) – empfohlen
cs.uniV(df, 'inc', weight='wghtpew').summary()
cs.ttest_u(..., weight='wghtpew', ...)
cs.regress('inc ~ sex', data=df, weight='wghtpew')

# Als pd.Series – bei fre() und fre_wl() erforderlich
cs.fre(df, 'inc', weight=df['wghtpew'])
cs.fre_wl(df, 'inc', dfL, weight=df['wghtpew'])
```

### Effekte der Gewichtung im ALLBUS

Im ALLBUS 2018/2019 gibt es zwei Gewichtungswerte:
- `wghtpew = 0.5448` für Ostdeutsche (ostdeutsche Stichprobe wird heruntergewichtet)
- `wghtpew = 1.2079` für Westdeutsche (westdeutsche Stichprobe wird hochgewichtet)

```python
# Ungewichtete Verteilung:
cs.fre(df, 'eastwest')
# → West: 68.65%, Ost: 31.35%

# Gewichtete Verteilung:
cs.fre(df, 'eastwest', weight=df['wghtpew'])
# → entspricht der tatsächlichen Bevölkerungsverteilung
```

---

## 5. Fehlende Werte

### cheatstat behandelt fehlende Werte automatisch

Alle Funktionen verwenden **Listwise Deletion** (vollständige Fälle):
Zeilen mit fehlenden Werten in den verwendeten Variablen werden
für die jeweilige Analyse ausgeschlossen.

```python
# Dieser Aufruf ist sicher auch mit NaN-Werten in 'inc':
cs.uniV(df, 'inc')    # n (gültig) wird korrekt ausgewiesen
cs.ttest_u(group='sex', g1=1.0, g2=2.0, dependent='inc', data=df)
# → verwendet nur Fälle ohne NaN in 'sex' und 'inc'
```

### Fehlende Werte vor der Analyse prüfen

```python
cs.missing_report(df).summary()
```

### Fehlende Werte mit `recode()` behandeln

```python
# Werte außerhalb des gültigen Bereichs als NaN kennzeichnen
df = cs.recode(df, 'inc', {
    '>0 and <=20000': 'valid',
    'else': np.nan
}, new_name='inc_clean')
```

---

## 6. Ergebnisse abrufen

### Universelles Zugriffsmuster

```python
# Schritt 1: Ergebnis erzeugen
result = cs.regress('inc ~ sex + educ', data=df)

# Schritt 2: Verfügbare Schlüssel anzeigen
print(result.keys())
# → ['stat', 'model', 'anova', 'Formel', 'Methode', ...]

# Schritt 3: Gewünschte Tabelle abrufen
koeffizienten = result['stat']
print(koeffizienten)

# Schritt 4: Als Excel exportieren
cs.export_results(result, 'meine_regression')
```

### Verfügbare Schlüssel je Funktion

| Funktion | Verfügbare Schlüssel |
|----------|---------------------|
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

## 7. Ausgabe und Export

### In Jupyter Notebook anzeigen

```python
# Direkte Anzeige als formatierte Tabelle
result = cs.uniV(df, 'inc')
result['stats']          # Wird automatisch als formatierte Tabelle angezeigt
```

### Tabelle als DataFrame weiterverarbeiten

```python
result = cs.regress('inc ~ sex + educ', data=df)
tabelle = result['stat']

# Als CSV speichern
tabelle.to_csv('regression.csv', sep=';', decimal=',', index=False)

# Als Excel speichern
tabelle.to_excel('regression.xlsx', index=False)
```

### Mit `export_results()` exportieren

```python
result = cs.regress('inc ~ sex + educ', data=df)

# Excel (Standard)
cs.export_results(result, 'regression_ergebnis')

# CSV
cs.export_results(result, 'regression_ergebnis', format='csv')

# LaTeX für wissenschaftliche Arbeiten
cs.export_results(result, 'regression_ergebnis', format='latex')

# HTML für Web-Berichte
cs.export_results(result, 'regression_ergebnis', format='html')
```

---

## 8. Tipps für Einsteiger

### Tipp 1: Immer mit `missing_report()` beginnen

```python
cs.missing_report(df).summary()
```

### Tipp 2: `summary()` für schnelle Übersicht

```python
cs.uniV(df, 'inc').summary()
cs.biV(df, 'sex', 'inc', 'ordinal').summary()
cs.regress('inc ~ sex + educ', data=df).summary()
```

### Tipp 3: `notable=True` für schnelle Statistiken

```python
# Nur Zusammenhangsmaße, keine Kreuztabelle
cs.biV(df, 'eastwest', 'pv19', scale='ordinal', notable=True).summary()
```

### Tipp 4: Variablentypen kennen

```python
# Prüfen, ob numerisch
print(df['sex'].dtype)        # float64 → numerisch
print(df['educ'].dtype)       # float64 → numerisch

# Eindeutige Werte anzeigen
print(df['sex'].unique())     # [1.0, 2.0]
print(df['educ'].unique())    # [1.0, 2.0, 3.0, ...]
```

### Tipp 5: Skalenniveau korrekt angeben

| Skalenniveau | `scale=` Parameter | Ausgabe |
|--------------|--------------------|---------|
| Nominal (Kategorien) | `'nominal'` oder `'n'` | Chi², G², Phi/Cramér's V |
| Ordinal oder metrisch | `'ordinal'` oder `'om'` | Pearson-r, Spearman-ρ, Kendall-τ, Somers' D |

### Tipp 6: Gruppennamen prüfen

```python
# Vor dem T-Test die Gruppenausprägungen prüfen
print(df['sex'].unique())    # [1.0, 2.0, nan]
# → g1=1.0, g2=2.0 (als Float, nicht als String!)

cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=df).summary()
```

### Tipp 7: Zwei DataFrames für Labels

```python
# df_num: numerische Werte für Analysen
# df_lab: Labels für Häufigkeitstabellen

cs.fre_wl(df_num, 'educ', df_lab)
```

---

*cheatstat Version 4.1.2 | Autor: Jürgen Leibold | März 2026*

[→ Nächste Seite: Beispiele](examples.md) |
[← Installation](installation.md) |
[← Zurück zur Übersicht](index.md)