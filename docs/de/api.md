# API-Referenz

[← Beispiele](examples.md) | [🇬🇧 English](../en/api.md) |
[← Zurück zur Übersicht](index.md)

---

## Inhaltsverzeichnis

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

Einheitlicher Container für alle Analyseergebnisse in cheatstat.

### Attribute

| Attribut | Typ | Beschreibung |
|----------|-----|-------------|
| `tables` | dict | Benannte DataFrames (z.B. `{'observed': df, ...}`) |
| `stat` | pd.DataFrame | Hauptergebnistabelle (Statistiken, Koeffizienten) |
| `test_name` | str | Name der Analyse |
| `info` | dict | Metadaten (n, Formel, Methode, ...) |

### Methoden

#### `.summary(show_tables=False)`

Gibt eine formatierte Zusammenfassung auf der Konsole aus.

```python
result.summary()                  # Nur Statistiken
result.summary(show_tables=True)  # Inkl. aller Tabellen
```

#### `['schlüssel']`

Dict-ähnlicher Zugriff auf Ergebnisse.

```python
result['stat']          # Statistik-DataFrame
result['observed']      # Tabelle per Name
result['R²']            # Info-Wert
```

#### `.keys()`

Gibt alle verfügbaren Schlüssel zurück.

```python
result.keys()    # ['stat', 'observed', 'col_percent', ...]
```

---

## missing_report

```
missing_report(df, threshold=5.0)
```

Erstellt einen Bericht über fehlende Werte für alle Spalten.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `threshold` | float | 5.0 | Warnschwelle in Prozent |

### Rückgabe

`StatResult` mit:
- `result['stat']`: Tabelle mit Variable, n (gültig), n (fehlend), % fehlend, Status
- `result.info`: Zusammenfassung (Gesamtzahl, Vollständige, Mit Fehlenden, ...)

### Beispiel

```python
cs.missing_report(A18N).summary()
cs.missing_report(A18N, threshold=10.0).summary()
```

---

## recode

```
recode(df, column, mapping, new_name=None, else_value=np.nan)
```

Rekodiert eine Variable nach einer Zuordnungstabelle.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `column` | str | – | Name der Quellspalte |
| `mapping` | dict | – | Zuordnung {Bedingung: Wert} |
| `new_name` | str | None | Name der Zielspalte (None = überschreiben) |
| `else_value` | any | np.nan | Wert für nicht zugeordnete Fälle |

### Mapping-Formate

| Format | Beispiel | Bedeutung |
|--------|---------|-----------|
| Komma-Werte | `'1,2,4'` | Exakt diese Werte |
| Bereich | `'1-6'` | Werte von 1 bis 6 |
| Größer als | `'>5'` | Werte > 5 |
| Kleiner gleich | `'<=3'` | Werte ≤ 3 |
| AND | `'>=2 and <=6'` | Werte zwischen 2 und 6 |
| OR | `'<2 or >8'` | Werte < 2 oder > 8 |
| NOT | `'not 5'` | Alle außer 5 |
| ELSE | `'else'` | Alle verbleibenden |
| Tupel | `(1, 6)` | Bereich 1–6 |
| Zahl | `5` | Exakter Wert 5 |

### Rückgabe

`pd.DataFrame` mit neuer/überschriebener Spalte.

### Beispiele

```python
# Einfach
df = cs.recode(df, 'educ', {'1,2': 1, '3,4': 2, '5': 3},
               new_name='educ3')

# Bereich
df = cs.recode(df, 'age', {'18-29': 1, '30-49': 2, '50-99': 3},
               new_name='age3')

# Komplex
df = cs.recode(df, 'inc', {'<1000': 1, '>=1000 and <3000': 2, '>=3000': 3},
               new_name='inc3')

# Invertieren
df = cs.recode(df, 'item1', {1: 5, 2: 4, 3: 3, 4: 2, 5: 1},
               new_name='item1_r')
```

---

## fre

```
fre(df, column, weight=None, sort=True, round_digits=2)
```

Erstellt eine Häufigkeitstabelle für eine Variable.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `column` | str | – | Name der Spalte |
| `weight` | str/pd.Series | None | Gewichtung (Spaltenname oder pd.Series) |
| `sort` | bool | True | Nach Wert aufsteigend sortieren |
| `round_digits` | int | 2 | Dezimalstellen für Prozentangaben |

### Rückgabe

`pd.DataFrame` mit Spalten:
- `Ausprägung`: Kategorien
- `Häufigkeiten`: Absolute Häufigkeiten
- `Prozent`: Prozentualer Anteil (inkl. fehlende)
- `kum. Prozente`: Kumulierter Prozentanteil
- `gültigeP`: Prozentualer Anteil (exkl. fehlende)
- `kum.gültigeP`: Kumulierter gültiger Prozentanteil

### Beispiele

```python
cs.fre(A18N, 'sex')
cs.fre(A18N, 'sex', weight='wghtpew')
cs.fre(A18N, 'pv19', sort=True, round_digits=1)
```

> **Hinweis:** `weight` kann nun entweder ein Spaltenname (str) oder eine pd.Series sein.

---

## fre_wl

```
fre_wl(df, column, labels, weight=None, sort_by_value=True, round_digits=2)
```

Erstellt eine Häufigkeitstabelle mit Wertelabels.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `column` | str | – | Name der Spalte |
| `labels` | pd.DataFrame/pd.Series | – | Wertelabels |
| `weight` | str/pd.Series | None | Gewichtung (Spaltenname oder pd.Series) |
| `sort_by_value` | bool | True | Nach Ausprägungswert sortieren |
| `round_digits` | int | 2 | Dezimalstellen |

### Rückgabe

`pd.DataFrame` mit Spalten:
- `Ausprägung`: Numerischer Wert
- `Label`: Wertelabel
- `Häufigkeiten`, `Prozent`, `kum. Prozente`, `gültigeP`, `kum.gültigeP`

### Beispiel

```python
cs.fre_wl(A18N, 'educ', A18L)
cs.fre_wl(A18N, 'pv19', A18L['pv19'], weight='wghtpew')
```

---

## uniV

```
uniV(df, column_name, weight=None, se=False)
```

Univariate Analyse: Häufigkeitstabelle + deskriptive Statistiken.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `column_name` | str | – | Spaltenname |
| `weight` | str/pd.Series | None | Gewichtung |
| `se` | bool | False | Standardfehler ausgeben |

### Rückgabe

`StatResult` mit:
- `result['fre']`: Häufigkeitstabelle (pd.DataFrame)
- `result['stats']` / `result['stat']`: Deskriptive Statistiken (pd.DataFrame)
- `result.info`: n (gesamt), n (gültig), n (effektiv bei Gewichtung)

### Deskriptive Statistiken

| Statistik | Beschreibung |
|-----------|-------------|
| Modus | Häufigster Wert |
| 25%-Quantil | Erstes Quartil |
| 50%-Quantil (Median) | Zentralwert |
| 75%-Quantil | Drittes Quartil |
| IQR | Interquartilsabstand |
| Mittelwert | Arithmetisches Mittel |
| 95%-KI (untere/obere Grenze) | Konfidenzintervall des Mittelwerts |
| Minimum / Maximum | Extremwerte |
| Varianz | Streuungsmaß |
| Standardabweichung | Streuungsmaß |
| Schiefe | Asymmetrie der Verteilung |
| Kurtosis | Wölbung der Verteilung |
| Exzess | Kurtosis − 3 |

### Beispiele

```python
cs.uniV(A18N, 'inc').summary()
cs.uniV(A18N, 'inc', weight='wghtpew').summary()
cs.uniV(A18N, 'inc', se=True).summary()

# Tabellen abrufen
result = cs.uniV(A18N, 'inc')
result['fre']     # Häufigkeitstabelle
result['stats']   # Statistiken
```

---

## cross_tab

```
cross_tab(df, col1, col2, weight=None, round_digits=2,
          show_expected=True, show_residuals=True,
          show_deff=True, show_deff_p=True)
```

Erstellt eine gewichtete Kreuztabelle.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `col1` | str | – | Zeilenvariable |
| `col2` | str | – | Spaltenvariable |
| `weight` | str/pd.Series | None | Gewichtung |
| `round_digits` | int | 2 | Dezimalstellen |
| `show_expected` | bool | True | Erwartete Häufigkeiten anzeigen |
| `show_residuals` | bool | True | Standardisierte Residuen anzeigen |
| `show_deff` | bool | True | Design-Effekt anzeigen |
| `show_deff_p` | bool | True | Korrigierten p-Wert anzeigen |

### Rückgabe

`StatResult` mit:
- `result['observed']`: Beobachtete Häufigkeiten
- `result['col_percent']`: Spaltenprozentuierung
- `result['row_percent']`: Zeilenprozentuierung
- `result['total_percent']`: Gesamtprozentuierung
- `result['expected']`: Erwartete Häufigkeiten
- `result['residuals']`: Einfache Residuen
- `result['st_residuals']`: Standardisierte Residuen
- `result['deff']`: Design-Effekt (nur bei Gewichtung)
- `result['p_value_deff']`: Korrigierter p-Wert (nur bei Gewichtung)

### Beispiele

```python
ct = cs.cross_tab(A18N, 'sex', 'eastwest')
ct.summary(show_tables=True)
ct['observed']         # Beobachtete Häufigkeiten
ct['col_percent']      # Spaltenprozentuierung

# Ohne Design-Effekt
ct = cs.cross_tab(A18N, 'sex', 'educ',
                  show_deff=False, show_deff_p=False)
```

---

## biV

```
biV(df, col1, col2, scale, weight=None, round_digits=2, notable=False)
```

Bivariate Analyse mit Zusammenhangsmaßen.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `col1` | str | – | Erste Variable |
| `col2` | str | – | Zweite Variable |
| `scale` | str | – | Skalenniveau (s.u.) |
| `weight` | str/pd.Series | None | Gewichtung |
| `round_digits` | int | 2 | Dezimalstellen |
| `notable` | bool | False | Nur Statistiken, keine Kreuztabelle |

### Scale-Parameter

| `scale=` | Erlaubte Werte | Berechnete Maße |
|----------|---------------|----------------|
| Nominal | `'nominal'`, `'n'`, `'kategorial'`, `'kat'` | Chi², G², Phi (2×2) / Cramér's V |
| Ordinal/metrisch | `'ordinal'`, `'om'`, `'metrisch'`, `'ordinal-metrisch'` | Pearson-r, Spearman-ρ, Kendall-τ, Somers' D |

### Rückgabe

`StatResult` mit:
- `result['stat']`: Zusammenhangsmaße mit p-Werten und Signifikanzsternen
- `result['cross_tab']`: Kreuztabelle (StatResult, wenn `notable=False`)

### Beispiele

```python
# Nominal
cs.biV(A18N, 'sex', 'eastwest', scale='nominal').summary()

# Ordinal
cs.biV(A18N, 'eastwest', 'pv19', scale='ordinal').summary()

# Nur Statistiken
cs.biV(A18N, 'sex', 'educ', scale='nominal', notable=True).summary()

# Mit Gewichtung
cs.biV(A18N, 'eastwest', 'pv19', scale='ordinal',
       weight='wghtpew').summary()
```

---

## ttest_u

```
ttest_u(group, g1, g2, dependent, data=None, weight=None,
        levene_test='median', autoLevene=True)
```

Unabhängiger t-Test für zwei Gruppen.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `group` | str | – | Name der Gruppenvariable |
| `g1` | int/float/str | – | Erste Gruppe |
| `g2` | int/float/str | – | Zweite Gruppe |
| `dependent` | str | – | Abhängige Variable |
| `data` | pd.DataFrame | None | Eingabedaten (**erforderlich**) |
| `weight` | str/pd.Series | None | Gewichtung |
| `levene_test` | str | `'median'` | Art des Levene-Tests: `'mean'`, `'median'`, `'trimmed'` |
| `autoLevene` | bool | True | Automatische Test-Entscheidung via Levene |

### Rückgabe

`StatResult` mit `result['stat']`:

| Statistik | Beschreibung |
|-----------|-------------|
| Test | Verwendeter Test (Student-t / Welch-t) |
| t-Statistik | t-Wert |
| p-Wert | Signifikanz |
| df | Freiheitsgrade (Welch-Satterthwaite) |
| Mittelwert G1/G2 | Mittelwerte der Gruppen |
| Differenz (G1-G2) | Mittelwertdifferenz |
| 95%-KI unten/oben | Konfidenzintervall der Differenz |
| Varianz G1/G2 | Gruppenvarianzen |
| Cohen's d | Effektstärke |
| n G1/G2 (roh/eff) | Stichprobengrößen |
| Levene p | p-Wert des Levene-Tests |

### Hinweis zur Entscheidungslogik

- `autoLevene=True` (Standard): Levene-Test entscheidet automatisch
  → p(Levene) > 0.05: Student-t | p(Levene) ≤ 0.05: Welch-t
- `autoLevene=False`: Immer Welch-t (empfohlen bei Gewichtung)
- Bei Gewichtung: Levene-Test wird nicht durchgeführt, Welch-t wird verwendet

### Beispiele

```python
# Standard
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N).summary()

# Mit Gewichtung
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N, weight='wghtpew').summary()

# Ohne automatische Entscheidung
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N, autoLevene=False).summary()

# Mit Levene-Variante 'mean'
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=A18N, levene_test='mean').summary()
```

---

## regress

```
regress(formula, data, weight=None, robust=False,
        show_beta=True, show_ci=True, show_vif=True)
```

OLS-Regression mit standardisierten Koeffizienten, VIF und 95%-KI.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `formula` | str | – | R-Formel: `'y ~ x1 + x2 + ...'` |
| `data` | pd.DataFrame | – | Eingabedaten |
| `weight` | str | None | Gewichtungsspalte → WLS |
| `robust` | bool | False | Robuste Standardfehler (HC3) |
| `show_beta` | bool | True | Standardisierte β anzeigen |
| `show_ci` | bool | True | 95%-KI anzeigen |
| `show_vif` | bool | True | VIF anzeigen |

### Formel-Syntax

| Syntax | Bedeutung |
|--------|-----------|
| `'y ~ x1 + x2'` | Einfache Regression |
| `'y ~ C(x1) + x2'` | x1 als kategoriale Variable |
| `'y ~ x1 + x2 + x1:x2'` | Mit Interaktionsterm |

### Rückgabe

`StatResult` mit:
- `result['stat']`: Koeffiziententabelle
- `result['model']`: statsmodels `RegressionResults`-Objekt
- `result['anova']`: ANOVA-Tabelle Typ 2
- `result.info`: R², adj. R², F, AIC, BIC, Durbin-Watson, ...

### Koeffiziententabelle

| Spalte | Beschreibung |
|--------|-------------|
| `Variable` | Prädiktorname |
| `b` | Unstandardisierter Koeffizient |
| `SE` | Standardfehler |
| `Beta (β)` | Standardisierter Koeffizient |
| `t` | t-Wert |
| `p-Wert` | Signifikanz |
| `Sig.` | Sterne (***/**/*/ n.s.) |
| `95%-KI unten/oben` | Konfidenzintervall |
| `VIF` | Variance Inflation Factor |

### VIF-Interpretation

| VIF | Bedeutung |
|-----|-----------|
| < 5 | Kein Problem |
| 5–10 | Moderate Multikollinearität ⚠️ |
| > 10 | Starke Multikollinearität 🔴 |

### Beispiele

```python
# Standard-OLS
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N).summary()

# WLS mit Gewichtung
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N,
           weight='wghtpew').summary()

# Robuste Standardfehler
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N,
           robust=True).summary()

# Kategoriale Variable
cs.regress('inc ~ sex + eastwest + C(iscd11)', data=A18N).summary()

# Ergebnis weiterverarbeiten
result = cs.regress('inc ~ sex + educ', data=A18N)
result['model'].resid          # Residuen
result['model'].fittedvalues   # Vorhergesagte Werte
result['anova']                # ANOVA-Tabelle
```

---

## beta

```
beta(formula, data, weight=None, full=False)
```

Berechnet standardisierte Regressionskoeffizienten (β).

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `formula` | str | – | R-Formel: `'y ~ x1 + x2 + ...'` |
| `data` | pd.DataFrame | – | Eingabedaten |
| `weight` | str/pd.Series | None | Gewichtung |
| `full` | bool | False | Vollständige Tabelle mit SE, t, p |

### Rückgabe

- `full=False`: `pd.Series` mit β-Koeffizienten (inkl. R², n als Attribute)
- `full=True`: `StatResult` mit vollständiger Regressionstabelle

### Beispiele

```python
# Einfach: nur β
b = cs.beta('inc ~ sex + eastwest + iscd11', data=A18N)
print(b)
print(f"R² = {b.attrs['R_squared']:.4f}")

# Vollständig: mit SE, t, p
cs.beta('inc ~ sex + eastwest + iscd11', data=A18N, full=True).summary()

# Mit Gewichtung
cs.beta('inc ~ sex + eastwest + iscd11', data=A18N,
        weight='wghtpew', full=True).summary()
```

---

## cronbach

```
cronbach(df, items, weight=None, item_analysis=True)
```

Berechnet Cronbach's Alpha und Item-Analyse.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `items` | list | – | Spaltennamen der Items |
| `weight` | str/pd.Series | None | Gewichtung (derzeit ungewichtet) |
| `item_analysis` | bool | True | Item-Total-Korrelationen berechnen |

### Rückgabe

`StatResult` mit:
- `result['stat']`: Item-Analyse-Tabelle (M, SD, r(it), Alpha ohne Item, Empfehlung)
- `result.info`: Alpha, Bewertung, k Items, n (Listwise)

### Alpha-Bewertung

| Alpha | Bewertung |
|-------|-----------|
| ≥ 0.90 | Exzellent |
| ≥ 0.80 | Gut |
| ≥ 0.70 | Akzeptabel |
| ≥ 0.60 | Fragwürdig |
| ≥ 0.50 | Schlecht |
| < 0.50 | Inakzeptabel |

### Beispiel

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

Berechnet und konvertiert Effektstärken.

### Parameter

| `test_type` | Pflichtparameter | Optionale Parameter |
|-------------|----------------|---------------------|
| `'cohen_d'` | `m1, m2, sd1, sd2` | `n1, n2` |
| `'eta_sq'` | `f, df1, df2` | – |
| `'omega_sq'` | `f, df1, df2` | `n` |
| `'r_to_d'` | `r` | – |
| `'d_to_r'` | `d` | – |
| `'odds_ratio'` | `a, b, c, d` | – |

### Effektstärke-Bewertung

| Maß | Klein | Mittel | Groß |
|-----|-------|--------|------|
| Cohen's d | 0.20 | 0.50 | 0.80 |
| r | 0.10 | 0.30 | 0.50 |
| Eta² | 0.01 | 0.06 | 0.14 |

### Beispiele

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

Prüft eine Variable auf Normalverteilung.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `column` | str | – | Spaltenname |

### Rückgabe

`StatResult` mit Tests:
- Shapiro-Wilk (nur bei n < 5.000)
- Kolmogorov-Smirnov
- Schiefe (z-standardisiert)
- Kurtosis (z-standardisiert)

### Beispiel

```python
cs.normality_test(A18N, 'inc').summary()
cs.normality_test(A18N, 'pv19').summary()
```

---

## compare_groups

```
compare_groups(df, group, variables, weight=None)
```

Vergleicht Mittelwerte mehrerer Variablen über Gruppen.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `group` | str | – | Gruppenvariable |
| `variables` | list | – | Zu vergleichende Variablen |
| `weight` | str/pd.Series | None | Gewichtung |

### Rückgabe

`StatResult` mit Tabelle: Mittelwert, SD, n für jede Gruppe und Variable.

### Beispiel

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

Exportiert Analyseergebnisse in eine Datei.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `result` | StatResult/pd.DataFrame | – | Zu exportierende Ergebnisse |
| `filename` | str | – | Dateiname **ohne** Endung |
| `format` | str | `'excel'` | Format: `'excel'`, `'csv'`, `'html'`, `'latex'` |
| `decimal` | str | `','` | Dezimaltrennzeichen (nur CSV) |

### Exportformate

| Format | Datei | Anwendung |
|--------|-------|-----------|
| `'excel'` | `.xlsx` | Excel, LibreOffice Calc |
| `'csv'` | `.csv` | R, SPSS, Tabellenverarbeitung |
| `'html'` | `.html` | Web-Berichte |
| `'latex'` | `.tex` | Wissenschaftliche Arbeiten |

### Beispiele

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

Erstellt Dummy-Variablen und hängt sie an den DataFrame.

### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|-------------|
| `df` | pd.DataFrame | – | Eingabedaten |
| `column` | str | – | Quellspalte (muss numerisch sein) |
| `prefix` | str | None | Präfix für Dummy-Spalten (Standard: Spaltenname) |

### Rückgabe

`pd.DataFrame` mit angehängten Dummy-Spalten.
Dezimalstellen werden entfernt (z.B. `educ_3` statt `educ_3.0`).

### Beispiele

```python
A18N = cs.create_dummies(A18N, 'educ', prefix='educ')
# → Neue Spalten: educ_1, educ_2, educ_3, educ_4, educ_5, educ_6, educ_7

A18N = cs.create_dummies(A18N, 'eastwest')
# → Neue Spalten: eastwest_1, eastwest_2
```

---

## help_cheatstat

```
help_cheatstat()
```

Gibt eine kompakte Kurzanleitung aller Funktionen auf der Konsole aus.

```python
cs.help_cheatstat()
```

---

*cheatstat Version 4.1 | Autor: Jürgen Leibold | März 2026*

[← Beispiele](examples.md) | [← Zurück zur Übersicht](index.md)