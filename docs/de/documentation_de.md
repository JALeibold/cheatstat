# cheatstat – Dokumentation (Version 4.1.2)

**Einfache statistische Funktionen für die Sozialwissenschaften**  
*Autor: Jürgen Leibold | Version 4.1.2 | März 2026 | Lizenz: MIT*

---

> [!WARNING]
> ## ⚠️ Wichtiger Hinweis zur Gewichtung
>
> **Diese Implementierung ist eine Approximation.**
>
> cheatstat bietet eine **vereinfachte Gewichtung**, die für explorative Analysen und Lehrzwecke geeignet ist. Es berücksichtigt jedoch **nicht** das vollständige Survey-Design (Primary Sampling Units, Strata), das für korrekte Standardfehler und Konfidenzintervalle in komplexen Survey-Daten wie dem ALLBUS erforderlich ist.
>
> **cheatstat ist NICHT geeignet für:**
> - Offizielle statistische Berichte
> - Wissenschaftliche Publikationen
> - Politische Entscheidungsgrundlagen
>
> **Für wissenschaftliche Publikationen** verwenden Sie bitte:
> - R-Pakete wie `survey` oder `srvyr`
> - SAS-Prozeduren wie `SURVEYMEANS` oder `SURVEYREG`
> - SPSS-Module wie "Complex Samples"
>
> **cheatstat ist ideal für:**
> - Lehrveranstaltungen in den Sozialwissenschaften
> - Explorative Datenanalyse
> - Schnelle Überprüfung von Hypothesen
> - Einstieg in statistische Methoden

---

## Inhaltsverzeichnis

1. [Einleitung](#einleitung)
2. [Installation und erste Schritte](#installation-und-erste-schritte)
3. [Daten vorbereiten](#daten-vorbereiten)
   - [Daten laden](#daten-laden)
   - [Fehlende Werte analysieren – `missing_report()`](#fehlende-werte-analysieren--missing_report)
   - [Variablen umkodieren – `recode()`](#variablen-umkodieren--recode)
4. [Deskriptive Statistik](#deskriptive-statistik)
   - [Häufigkeitstabellen – `fre()`](#häufigkeitstabellen--fre)
   - [Häufigkeitstabellen mit Labels – `fre_wl()`](#häufigkeitstabellen-mit-labels--fre_wl)
   - [Univariate Analyse – `uniV()`](#univariate-analyse--univ)
5. [Bivariate Analyse](#bivariate-analyse)
   - [Kreuztabellen – `cross_tab()`](#kreuztabellen--cross_tab)
   - [Zusammenhangsmaße – `biV()`](#zusammenhangsmaße--biv)
   - [T-Test – `ttest_u()`](#t-test--ttest_u)
6. [Multivariate Analyse](#multivariate-analyse)
   - [Regression – `regress()`](#regression--regress)
   - [Standardisierte Koeffizienten – `beta()`](#standardisierte-koeffizienten--beta)
   - [Reliabilitätsanalyse – `cronbach()`](#reliabilitätsanalyse--cronbach)
7. [Effektstärken und Diagnostik](#effektstärken-und-diagnostik)
   - [Effektstärken berechnen – `effect_size()`](#effektstärken-berechnen--effect_size)
   - [Normalverteilung prüfen – `normality_test()`](#normalverteilung-prüfen--normality_test)
   - [Deskriptiver Gruppenvergleich – `compare_groups()`](#deskriptiver-gruppenvergleich--compare_groups)
8. [Ergebnisse exportieren – `export_results()`](#ergebnisse-exportieren--export_results)
9. [Hilfsfunktionen](#hilfsfunktionen)
   - [`describe_df()`](#describe_df)
   - [`create_dummies()`](#create_dummies)
   - [`help_cheatstat()`](#help_cheatstat)
10. [Typische Workflows](#typische-workflows)
11. [Anhang](#anhang)
    - [ALLBUS-Variablenreferenz](#allbus-variablenreferenz)
    - [Signifikanzsterne](#signifikanzsterne)
    - [Effektstärken-Bewertung](#effektstärken-bewertung)
    - [Fehlerbehebung](#fehlerbehebung)

---

## Einleitung

cheatstat ist ein Python-Paket, das speziell für Studierende und Forschende in den Sozialwissenschaften entwickelt wurde. Es vereinfacht die Durchführung grundlegender statistischer Analysen mit Survey-Daten wie dem ALLBUS, GESIS-Sozialerhebungen oder anderen repräsentativen Bevölkerungsumfragen.

### Warum cheatstat?

Sozialwissenschaftler:innen stehen oft vor folgenden Herausforderungen:

| Herausforderung | Lösung in cheatstat |
|---|---|
| Komplexe Survey-Gewichtung: Viele Pakete ignorieren Survey-Gewichtung oder implementieren sie unvollständig | Einheitliche Handhabung von Survey-Gewichtung in allen Funktionen (für explorative Zwecke) |
| Umkodieren von Variablen: In Python oft umständlich, besonders bei komplexen Bedingungen | Intuitive Umcodierungsfunktionen mit Unterstützung für komplexe Bedingungen |
| Interpretation von Ergebnissen: Statistische Ausgaben sind oft zu technisch für Einsteiger | Klare, interpretierbare Ausgaben mit Signifikanzsternen und Bewertungen |
| Berichterstattung: Ergebnisse müssen in einer für sozialwissenschaftliche Publikationen geeigneten Form vorliegen | Direkter Export in Formate für wissenschaftliche Berichte |

> *"cheatstat ist nicht das mächtigste Statistikpaket für Python, aber es ist das beste für Sozialwissenschaftler:innen, die schnell und korrekt arbeiten müssen – im Rahmen explorativer Analysen."*

---

## Installation und erste Schritte

### Installation

cheatstat kann über pip installiert werden:

```
pip install cheatstat
```

Für die vollständige Funktionalität (insbesondere Regression) wird empfohlen, zusätzlich `statsmodels` zu installieren:

```
pip install statsmodels
```

**Abhängigkeiten:**

| Paket | Typ | Verwendung |
|---|---|---|
| pandas | Pflicht | Datenverarbeitung |
| numpy | Pflicht | Numerische Berechnungen |
| scipy | Pflicht | Statistische Tests |
| statsmodels | Optional | `regress()`, `beta()` |
| numba | Optional | Geschwindigkeitsoptimierung |

**Systemvoraussetzungen:** Python ≥ 3.9

### Import

Nach der Installation importieren Sie cheatstat wie folgt:

```python
import cheatstat as cs
```

Dies ist die empfohlene Importmethode, da sie alle Funktionen unter dem Präfix `cs.` verfügbar macht und Kollisionen mit anderen Paketen vermeidet.

---

## Daten vorbereiten

### Daten laden

Für die folgenden Beispiele wird der ALLBUS 2018/2019 verwendet. Die Daten können von der GESIS-Website heruntergeladen werden.

```python
import pandas as pd
import pyreadstat

# Rohdaten laden (ohne kategoriale Codierung)
A18N = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "isco08", "eastwest", "iscd11", "lm02", "age",
             "scage", "educ", "pv19", "pr04", "pr05", "pr07", "wghtpew"],
    convert_categoricals=False
)

# Daten mit Wertelabels laden
A18L = pd.read_spss(
    'ALLBUS2018.sav',
    usecols=["sex", "inc", "isco08", "eastwest", "iscd11", "lm02", "age",
             "scage", "educ", "pv19", "pr04", "pr05", "pr07", "wghtpew"],
    convert_categoricals=True
)
```

> **Hinweis:** `A18N` enthält numerische Werte (z.B. `1.0` für männlich), während `A18L` kategoriale Variablen mit Wertelabels enthält (z.B. `"MAENNLICH"`). Dies ist wichtig für die Funktionen `fre_wl()` und `recode()`.

---

### Fehlende Werte analysieren – `missing_report()`

Bevor Sie mit der Analyse beginnen, sollten Sie immer einen Überblick über fehlende Werte gewinnen.

```python
cs.missing_report(A18N).summary()
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
- Die Variable `scage` (Alter des Ehepartners) hat 44,90 % fehlende Werte – dies ist kritisch
- Die Variable `inc` (Einkommen) hat 11,07 % fehlende Werte – dies ist kritisch
- Die Variablen `pr04`, `pr05`, `pr07`, `lm02` und `pv19` haben zwischen 5,29 % und 8,66 % fehlende Werte
- Die Variablen `iscd11`, `age` und `educ` haben weniger als 1 % fehlende Werte
- Die Variablen `eastwest`, `sex` und `wghtpew` sind vollständig

**Praktische Tipps:**
- Variablen mit über 10 % fehlenden Werten sollten kritisch geprüft werden
- Bei kritischen Variablen wie `inc` (Einkommen) sollten Sie prüfen, ob die fehlenden Werte systematisch sind
- Für die weitere Analyse können Sie entweder listwise deletion verwenden oder Imputation durchführen

---

### Variablen umkodieren – `recode()`

In sozialwissenschaftlichen Analysen müssen Variablen häufig umkodiert werden, um Hypothesen zu testen. Die `recode()`-Funktion ist extrem flexibel und unterstützt:

| Syntax | Beschreibung | Beispiel |
|---|---|---|
| `'1,2,4,6'` | Komma-getrennte Werte | Mehrere Ausprägungen zusammenfassen |
| `'1-6'` | Bereiche mit Bindestrich | Wertebereich angeben |
| `'>5'`, `'>=5'`, `'<3'` | Vergleichsoperatoren | Schwellenwertbedingungen |
| `'>2 and <8'` | Logische Verknüpfung (und) | Beide Bedingungen müssen zutreffen |
| `'<2 or >8'` | Logische Verknüpfung (oder) | Eine der Bedingungen muss zutreffen |
| `'not 5'`, `'not 1,2,3'` | Negation | Alle Werte außer den genannten |
| `'else'` | Default-Wert | Alle restlichen Werte |

**Beispiel 1: Einfache Umcodierung von Bildung**

```python
# Originalkodierung:
# 1 = NO CERTIFICATE, 2 = LOWEST LEVEL, 3 = INTERMEDIARY LEVEL
# 4 = QUALI.UNIV.APPL.SCI., 5 = QUALI.FOR UNIVERSITY
# 6 = OTHER SCHOOL CERTIF., 7 = STILL AT SCHOOL

A18N = cs.recode(A18N, 'educ', {
    '1,2': 1,  # niedrig
    '3,4': 2,  # mittel
    '5': 3     # hoch
}, new_name='educ3')
```

**Beispiel 2: Alterskategorien erstellen**

```python
A18N = cs.recode(A18N, 'age', {
    '18-29': 1,  # jung
    '30-49': 2,  # mittel
    '50-99': 3   # alt
}, new_name='age_kat')
```

**Beispiel 3: Komplexe Bedingungen**

```python
# Ostdeutsche (eastwest=1) mit niedrigem Einkommen (inc<2000) als Gruppe identifizieren
A18N = cs.recode(A18N, 'eastwest', {
    '1 and inc<2000': 1,  # Ostdeutschland mit niedrigem Einkommen
    '1 and inc>=2000': 2, # Ostdeutschland mit hohem Einkommen
    '2': 3                # Westdeutschland
}, new_name='ostwest_eink')
```

**Beispiel 4: Likert-Skala invertieren**

```python
# pv19: Wahrscheinlichkeit CDU/CSU zu wählen (1=VERY UNLIKELY, 10=VERY LIKELY)
# Für die Analyse soll die Skala invertiert werden
A18N = cs.recode(A18N, 'pv19', {
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

**Beispiel 5: Fehlende Werte kennzeichnen**

```python
# inc: Einkommen - fehlende Werte explizit kennzeichnen
A18N = cs.recode(A18N, 'inc', {
    'not 0-18000': np.nan,  # Alle Werte außerhalb des Bereichs als fehlend
    'else': 'inc'           # Alle anderen Werte beibehalten
}, new_name='inc_clean')
```

> **Tipps für die Praxis:**
> - Verwenden Sie immer `new_name`, um die Originalvariable zu erhalten
> - Dokumentieren Sie jede Umcodierung in Ihrem Analyseprotokoll
> - Prüfen Sie nach der Umcodierung mit `uniV()` die Ergebnisse

---

## Deskriptive Statistik

### Häufigkeitstabellen – `fre()`

Erstellt eine gewichtete Häufigkeitstabelle für eine Variable.

**Beispiel: Häufigkeitstabelle für Geschlecht**

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

**Interpretation:**
- Die Variable `sex` hat zwei Ausprägungen: `1.0` (männlich) und `2.0` (weiblich)
- 50,99 % der Befragten sind männlich, 49,01 % sind weiblich
- Es gibt keine fehlenden Werte (`n-nan=` entspricht `n=`)

---

### Häufigkeitstabellen mit Labels – `fre_wl()`

Erstellt eine Häufigkeitstabelle mit Wertelabels. Benötigt zwei DataFrames: einen mit numerischen Werten (`A18N`) und einen mit Labels (`A18L`).

**Beispiel: Geschlecht mit Labels**

```python
cs.fre_wl(A18N, "sex", A18L, sort_by_value=True, round_digits=2)
```

```
  Ausprägung   Label  Häufigkeiten Prozent kum. Prozente gültigeP kum.gültigeP
0        1.0    MALE          1773   50.99         50.99    50.99        50.99
1        2.0  FEMALE          1704   49.01         100.0    49.01        100.0
2      Summe     ---          3477     ---           ---      ---          ---
3     n-nan=     ---          3477     ---           ---      ---          ---
```

**Beispiel: Bildungsabschluss mit Labels**

```python
cs.fre_wl(A18N, "educ", A18L, sort_by_value=True, round_digits=2)
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
- 34,37 % der Befragten haben einen INTERMEDIARY LEVEL (Realschulabschluss)
- 30,92 % haben QUALI.FOR UNIVERSITY (Abitur)
- 23,30 % haben LOWEST LEVEL (Hauptschulabschluss)
- Nur 1,44 % haben NO CERTIFICATE (keinen Schulabschluss)

> **Praxistipp:** Bei Likert-Skalen (z.B. `pv19`) ist `fre_wl()` besonders nützlich, da Sie die Antwortkategorien direkt sehen.

---

### Univariate Analyse – `uniV()`

Führt eine umfassende univariate Analyse durch, einschließlich Häufigkeitstabelle und deskriptiver Statistiken.

**Beispiel: Einkommensanalyse**

```python
result = cs.uniV(A18N, 'inc', se=False)
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
- Der Median des Einkommens liegt bei 1.500 €, der Mittelwert bei 1.825,89 €
- Das 95 %-Konfidenzintervall für den Mittelwert ist [1.779,31; 1.872,47]
- Die Verteilung ist stark rechtsschief (Schiefe = 2,95)
- Die Kurtosis ist positiv (19,01), was auf eine spitzere Verteilung als die Normalverteilung hindeutet
- Die hohe Schiefe und Kurtosis deuten auf eine nicht-normalverteilte Variable hin

**Mit Standardfehlern:**

```python
cs.uniV(A18N, 'inc', se=True).summary()
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

> **Praxistipp:** Der Standardfehler des Mittelwerts (22,82) gibt an, wie genau der Stichprobenmittelwert den Populationsmittelwert schätzt.

**Beispiel: Politische Einstellung (`pv19`)**

```python
cs.uniV(A18N, 'pv19', se=False).summary()
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
- Der Median der politischen Einstellung (Wahrscheinlichkeit CDU/CSU zu wählen) liegt bei 6,0
- Der Mittelwert liegt bei 5,60
- Die Verteilung ist leicht linksschief (Schiefe = −0,11)
- Die Kurtosis ist negativ (−1,43), was auf eine flachere Verteilung als die Normalverteilung hindeutet
- Die Verteilung ist annähernd symmetrisch

---

## Bivariate Analyse

### Kreuztabellen – `cross_tab()`

Erstellt eine gewichtete Kreuztabelle mit verschiedenen Prozentuierungen und Residuen.

**Beispiel: Geschlecht nach Wohnort (Ost/West)**

```python
ct = cs.cross_tab(A18N, 'sex', 'eastwest')
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
- Die beobachteten Häufigkeiten (`observed`) zeigen die Verteilung der Befragten
- Die Spaltenprozentuierung (`col_percent`) zeigt, dass in Ost und West fast gleich viele Männer und Frauen befragt wurden
- Die Residuen sind klein, was auf einen schwachen Zusammenhang hindeutet
- Der Chi²-Test bestätigt dies (siehe `biV()`-Ausgabe)

---

### Zusammenhangsmaße – `biV()`

Führt eine bivariate Analyse durch und berechnet Zusammenhangsmaße basierend auf dem Skalenniveau.

**Beispiel 1: Nominalskalierte Variablen (Ost/West nach Geschlecht)**

```python
cs.biV(A18N, "eastwest", "sex", scale="nominal").summary()
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
- Chi² und G² sind nicht signifikant (p > 0,05)
- Phi (φ) ist nahe 0, was auf keinen Zusammenhang hindeutet
- Geschlecht und Wohnort (Ost/West) sind unabhängig

**Beispiel 2: Ordinalskalierte Variablen (Ost/West nach politischer Einstellung)**

```python
cs.biV(A18N, "eastwest", "pv19", scale="ordinal").summary()
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
- Alle Zusammenhangsmaße sind negativ und signifikant (p < 0,001)
- Ostdeutsche tendieren zu niedrigeren Werten auf `pv19` (geringere Zustimmung zu CDU/CSU)
- Der Zusammenhang ist schwach (r = −0,10)
- Somers' D (Y|X) = −0,0571 bedeutet, dass die Vorhersage von `pv19` aus `eastwest` um 5,71 % verbessert wird

> **Praxistipp:** Für ordinalskalierte Variablen wie `pv19` (politische Einstellung auf Likert-Skala) sind Spearman-Rho und Kendall's Tau-b die angemessensten Maße.

---

### T-Test – `ttest_u()`

Führt einen unabhängigen t-Test für zwei Gruppen durch.

**Beispiel: Einkommensunterschiede nach Geschlecht (ungewichtet)**

```python
cs.ttest_u(group='sex', g1=1.0, g2=2.0, dependent='inc', data=A18N).summary()
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
- Der t-Test ist hoch signifikant (p < 0,001); Männer verdienen im Durchschnitt 809,79 € mehr als Frauen
- Der Effekt ist mittel bis groß (Cohen's d = 0,64)
- Das 95 %-Konfidenzintervall für die Differenz ist [722,90; 896,68]
- Der Levene-Test zeigt signifikante Unterschiede in den Varianzen (p < 0,001), daher wurde der Welch-t-Test verwendet
- Die Varianz ist bei Männern (2.308.618,97) deutlich höher als bei Frauen (788.126,64)

**Mit Survey-Gewichtung:**

```python
cs.ttest_u(group='sex', g1=1.0, g2=2.0, dependent='inc',
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
- Mit Gewichtung ist der Unterschied noch größer: Männer verdienen im Durchschnitt 891,93 € mehr
- Der Effekt ist etwas größer (Cohen's d = 0,69)
- Die effektive Stichprobengröße ist geringer als die rohe Stichprobengröße (1.474,97 vs. 1.614 für Männer)
- Die Gewichtung verstärkt den Unterschied, was darauf hindeutet, dass die ungewichtete Analyse den Unterschied unterschätzt

> **Praxistipp:** Bei Survey-Daten wie dem ALLBUS sollten Sie immer die Gewichtung verwenden, um repräsentative Ergebnisse zu erhalten. Beachten Sie jedoch, dass cheatstat nur eine vereinfachte Gewichtung bietet.

---

## Multivariate Analyse

### Regression – `regress()`

Führt eine OLS-Regression durch und ergänzt die Ausgabe um standardisierte Beta-Koeffizienten.

**Beispiel: Einkommen nach Geschlecht, Ost/West und Bildung (OLS, ungewichtet)**

```python
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N).summary()
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
- Der Regressionskoeffizient für `sex` ist −720,77: Männer (1.0) verdienen im Durchschnitt 720,77 € mehr als Frauen (2.0), kontrolliert für Wohnort und Bildung
- Der Koeffizient für `eastwest` ist −395,87: Ostdeutsche (1.0) verdienen im Durchschnitt 395,87 € weniger als Westdeutsche (2.0)
- Der Koeffizient für `iscd11` ist 288,15: Pro Bildungskategorie erhöht sich das Einkommen um 288,15 €
- Alle Koeffizienten sind hoch signifikant (p < 0,001)
- Das Modell erklärt 26,49 % der Varianz des Einkommens (R² = 0,2649)
- Der standardisierte Koeffizient für `iscd11` (0,39) ist am größten und weist auf den stärksten Effekt hin

**Mit Gewichtung und robusten Standardfehlern:**

```python
cs.regress('inc ~ sex + eastwest + iscd11', data=A18N,
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
- Mit Gewichtung und robusten Standardfehlern sind die Effekte etwas größer
- Der Geschlechtseffekt erhöht sich von −720,77 auf −791,91 €
- Der Ost-West-Unterschied bleibt ähnlich (−394,37 €)
- Das Modell erklärt nun 26,83 % der Varianz (R² = 0,2683)

**Mit kategorialer Variable:**

```python
cs.regress('inc ~ sex + eastwest + C(iscd11)', data=A18N).summary()
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
- Die Referenzkategorie ist `iscd11=1.0` (PRIMARY EDUCATION)
- Befragte mit `iscd11=8.0` (DOCTORAL LEVEL) verdienen im Durchschnitt 3.127,25 € mehr als die Referenzgruppe
- Der VIF-Wert für `iscd11=7.0` (MASTER LEVEL) ist mit 20,13 kritisch – dies deutet auf Multikollinearität hin

> **Praxistipp:** Die VIF-Werte (Variance Inflation Factor) zeigen auf Multikollinearität. Werte über 5 (gelb markiert) oder 10 (rot markiert) sind kritisch. Bei kategorialen Variablen wie `iscd11` ist Multikollinearität häufig, da die Kategorien korreliert sind.

---

### Standardisierte Koeffizienten – `beta()`

Berechnet nur die standardisierten Regressionskoeffizienten (nützlich für schnelle Vergleiche).

```python
cs.beta('inc ~ sex + eastwest + iscd11', data=A18N, full=True).summary()
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
- Der standardisierte Koeffizient für `sex` ist −0,27: Eine Standardabweichungs-Änderung in `sex` führt zu einer 0,27-Standardabweichungs-Änderung im Einkommen
- `iscd11` hat den größten Effekt (β = 0,39)
- Die bivariaten Korrelationen (`r(y,x)`) zeigen die unkontrollierten Zusammenhänge
- Die Differenz zwischen β und r zeigt den Einfluss der Kontrolle für andere Variablen

---

### Reliabilitätsanalyse – `cronbach()`

Berechnet Cronbach's Alpha für eine Skala.

**Beispiel: Reliabilität einer Einstellungsskala**

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

**Interpretation:**
- Cronbach's Alpha = −0,2415 ist negativ und wird als "inakzeptabel" bewertet
- Alle Item-Total-Korrelationen sind negativ, was auf ein Problem mit der Skalenbildung hindeutet
- Alle Items sollten entfernt werden, da sie die Reliabilität verschlechtern
- Mögliche Ursachen: falsche Richtung der Items oder keine gemeinsame Dimension

> **Praxistipp:** Negative Cronbach's Alpha-Werte deuten auf ein schwerwiegendes Problem mit der Skalenbildung hin. Prüfen Sie, ob alle Items in die gleiche Richtung kodiert sind.

---

## Effektstärken und Diagnostik

### Effektstärken berechnen – `effect_size()`

Berechnet gängige Effektstärken und konvertiert zwischen verschiedenen Maßen.

**Beispiel 1: Cohen's d aus Mittelwerten**

```python
cs.effect_size('cohen_d', m1=3250, m2=3000, sd1=1100, sd2=1050).summary()
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
- Cohen's d = 0,23 wird als "kleiner" Effekt bewertet
- Dies entspricht einer Korrelation von r = 0,12

**Beispiel 2: Konvertierung von r zu d**

```python
cs.effect_size('r_to_d', r=0.12).summary()
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

**Beispiel 3: Odds Ratio aus 2×2-Tabelle**

```python
cs.effect_size('odds_ratio', a=30, b=10, c=20, d=40).summary()
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
- Die Odds Ratio ist 6,00, was bedeutet, dass die Odds in Gruppe A sechsmal so hoch sind wie in Gruppe B
- Das 95 %-Konfidenzintervall [2,25; 16,00] enthält nicht 1, also ist der Unterschied signifikant

---

### Normalverteilung prüfen – `normality_test()`

Prüft eine Variable auf Normalverteilung.

```python
cs.normality_test(A18N, 'inc').summary()
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
- Sowohl Shapiro-Wilk als auch Kolmogorov-Smirnov zeigen signifikante Abweichungen von der Normalverteilung
- Die Verteilung ist stark rechtsschief (Schiefe = 2,95)
- Die Kurtosis ist positiv (19,01), was auf eine spitzere Verteilung als die Normalverteilung hindeutet

> **Praxistipp:** Bei großen Stichproben (n > 500) sind Normalverteilungstests oft zu empfindlich. Konzentrieren Sie sich auf die grafische Prüfung und die Schiefe/Kurtosis. Für das Einkommen ist eine nicht-normalverteilte Verteilung typisch.

---

### Deskriptiver Gruppenvergleich – `compare_groups()`

Vergleicht Mittelwerte mehrerer Variablen über Gruppen hinweg.

```python
cs.compare_groups(A18N, 'sex', ['inc', 'age', 'educ']).summary()
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
- Männer verdienen im Durchschnitt mehr (2.212,97 € vs. 1.403,18 €)
- Frauen sind im Durchschnitt etwas älter (51,95 vs. 51,42 Jahre)
- Der Bildungsabschluss ist ähnlich (3,49 vs. 3,48)

---

## Ergebnisse exportieren – `export_results()`

Exportiert Ergebnisse in verschiedene Formate.

**Beispiel: Regressionsergebnisse exportieren**

```python
result = cs.regress('inc ~ sex + eastwest + iscd11', data=A18N)
cs.export_results(result, 'regression_ergebnis', format='excel')
```

Dies erstellt eine Excel-Datei `regression_ergebnis.xlsx` mit mehreren Sheets:
- **Statistiken:** Die Koeffiziententabelle
- **Info:** Zusätzliche Informationen zum Modell

**Unterstützte Formate:**

| Format | Beschreibung | Verwendung |
|---|---|---|
| `excel` | Excel-Datei mit mehreren Sheets | Datenaufbereitung, Präsentationen |
| `csv` | Separate CSV-Dateien je Tabelle | Weiterverarbeitung mit anderen Tools |
| `html` | HTML-Datei | Web-Präsentationen |
| `latex` | LaTeX-Datei | Wissenschaftliche Manuskripte |

> **Praxistipp:** Für wissenschaftliche Arbeiten ist das LaTeX-Format besonders nützlich, da die Tabellen direkt in das Manuskript eingefügt werden können.

---

## Hilfsfunktionen

### `describe_df()`

Gibt eine Übersicht über alle Variablen im DataFrame aus (Typ, Anzahl gültiger Werte, fehlende Werte, Wertebereich).

### `create_dummies()`

Erstellt Dummy-Variablen aus einer kategorialen Variable.

### `help_cheatstat()`

Zeigt eine integrierte Hilfe mit einer Übersicht aller Funktionen und deren Parametern.

```python
cs.help_cheatstat()
```

---

## Typische Workflows

### Workflow 1: Deskriptive Analyse einer Variablen

```python
# 1. Fehlende Werte prüfen
cs.missing_report(A18N).summary()

# 2. Häufigkeitstabelle erstellen
cs.fre(A18N, 'pv19', sort=True).summary()

# 3. Mit Wertelabels (wenn verfügbar)
cs.fre_wl(A18N, 'pv19', A18L, sort_by_value=True).summary()

# 4. Univariate Analyse mit Statistiken
cs.uniV(A18N, 'pv19', se=True).summary()
```

### Workflow 2: Zusammenhangsanalyse

```python
# 1. Kreuztabelle erstellen
ct = cs.cross_tab(A18N, 'eastwest', 'pv19')
ct.summary(show_tables=True)

# 2. Zusammenhangsmaße berechnen
cs.biV(A18N, 'eastwest', 'pv19', scale='ordinal').summary()

# 3. Effektstärke berechnen
result = cs.biV(A18N, 'eastwest', 'pv19', scale='ordinal', notable=True)
d = result['stat'].loc[result['stat']['Maß'] == "Somers' D (Y|X)", 'Wert'].values[0]
cs.effect_size('d_to_r', d=float(d)).summary()
```

### Workflow 3: Regression mit Gewichtung

```python
# 1. Variablen umkodieren (wenn nötig)
A18N = cs.recode(A18N, 'educ', {'1,2': 1, '3,4': 2, '5': 3}, new_name='educ3')

# 2. Regression durchführen
result = cs.regress('inc ~ sex + eastwest + educ3',
                    data=A18N, weight='wghtpew', robust=True)

# 3. Ergebnisse anzeigen
result.summary()

# 4. Ergebnisse exportieren
cs.export_results(result, 'regression_inc', format='latex')
```

### Workflow 4: Reliabilitätsanalyse einer Skala

```python
# 1. Items einzeln prüfen
cs.uniV(A18N, 'item1').summary()
cs.uniV(A18N, 'item2').summary()
# ... für alle Items

# 2. Reliabilitätsanalyse durchführen
cronbach_result = cs.cronbach(A18N, ['pr04', 'pr05', 'pr07'])

# 3. Ergebnisse anzeigen
cronbach_result.summary()

# 4. Skalenvariable erstellen
A18N = cs.create_index(A18N, ['pr04', 'pr05', 'pr07'],
                       new_name='zufriedenheit')
```

---

## Anhang

### ALLBUS-Variablenreferenz

| Variable | Beschreibung | Skalenniveau | Wertebereich |
|---|---|---|---|
| `sex` | Geschlecht | nominal | 1.0 = Mann, 2.0 = Frau |
| `inc` | Einkommen | metrisch | 25–18.000 € |
| `eastwest` | Wohnort | nominal | 1.0 = Ost, 2.0 = West |
| `iscd11` | Beruf (ISCED 2011) | ordinal | 1–8 |
| `lm02` | Fernsehdauer pro Tag | metrisch | 1–1.200 Minuten |
| `age` | Alter | metrisch | 18–95 Jahre |
| `scage` | Schulabschluss (Ehepartner) | ordinal | 1–7 |
| `educ` | Bildungsabschluss | ordinal | 1–7 |
| `pv19` | Wahrscheinlichkeit CDU/CSU zu wählen | ordinal | 1–10 (Likert) |
| `pr04` | Wiedervereinigung: mehr Vorteile für Westen | ordinal | 1–4 |
| `pr05` | Wiedervereinigung: mehr Vorteile für Osten | ordinal | 1–4 |
| `pr07` | Bürger im anderen Teil der BRD fremd? | ordinal | 1–4 |
| `wghtpew` | Personengewicht | metrisch | 0,54–1,21 |

**Wertelabels für wichtige Variablen:**

*educ (Bildungsabschluss):*

| Wert | Label |
|---|---|
| 1.0 | NO CERTIFICATE |
| 2.0 | LOWEST LEVEL |
| 3.0 | INTERMEDIARY LEVEL |
| 4.0 | QUALI.UNIV.APPL.SCI. |
| 5.0 | QUALI.FOR UNIVERSITY |
| 6.0 | OTHER SCHOOL CERTIF. |
| 7.0 | STILL AT SCHOOL |

*pv19 (Wahrscheinlichkeit CDU/CSU zu wählen):*

| Wert | Label |
|---|---|
| 1.0 | VERY UNLIKELY |
| 2.0–9.0 | (Zwischenwerte) |
| 10.0 | VERY LIKELY |

*pr04 / pr05 / pr07:*

| Wert | Label |
|---|---|
| 1.0 | COMPLETELY AGREE |
| 2.0 | TEND TO AGREE |
| 3.0 | TEND TO DISAGREE |
| 4.0 | COMPLETELY DISAGREE |

---

### Signifikanzsterne

| Symbol | p-Wert | Interpretation |
|---|---|---|
| `***` | < 0,001 | hoch signifikant |
| `**` | < 0,01 | signifikant |
| `*` | < 0,05 | tendenziell signifikant |
| `n.s.` | ≥ 0,05 | nicht signifikant |

---

### Effektstärken-Bewertung

| Maß | klein | mittel | groß |
|---|---|---|---|
| Cohen's d | 0,2 | 0,5 | 0,8 |
| r | 0,1 | 0,3 | 0,5 |
| Eta² | 0,01 | 0,06 | 0,14 |
| Omega² | 0,01 | 0,06 | 0,14 |
| Phi / Cramér's V | 0,1 | 0,3 | 0,5 |

---

### Fehlerbehebung

**Problem:** `ValueError: Gewichtungsspalte 'wghtpew' nicht gefunden`

> Lösung: Prüfen Sie, ob die Gewichtungsspalte im DataFrame vorhanden ist:
> ```python
> print(A18N.columns)
> ```

**Problem:** `ValueError: Gruppe '3.0' existiert nicht in der Variable 'sex'`

> Lösung: Prüfen Sie die vorhandenen Gruppen:
> ```python
> print(A18N['sex'].unique())
> ```

**Problem:** `LinAlgError: Singular matrix`

> Lösung: Es gibt perfekte Multikollinearität zwischen Prädiktoren. Prüfen Sie mit `cs.cronbach()` oder entfernen Sie redundante Variablen.

**Problem:** Cronbach's Alpha negativ

> Lösung: Prüfen Sie, ob alle Items in die gleiche Richtung kodiert sind. Möglicherweise müssen einige Items invertiert werden (siehe `recode()`).

---

## Schlussbemerkung

cheatstat wurde entwickelt, um die statistische Analyse in den Sozialwissenschaften zugänglicher zu machen. Es vereinfacht die häufigsten Analyse-Schritte, ohne dabei die statistische Korrektheit zu vernachlässigen. Besonders bei Survey-Daten wie dem ALLBUS ist die native Unterstützung von Gewichtung ein entscheidender Vorteil gegenüber anderen Python-Paketen.

> **Wichtiger Hinweis:** cheatstat bietet eine vereinfachte Gewichtung, die für explorative Analysen und Lehrzwecke geeignet ist. Es berücksichtigt jedoch nicht das vollständige Survey-Design (Primary Sampling Units, Strata), das für korrekte Standardfehler und Konfidenzintervalle in komplexen Survey-Daten wie dem ALLBUS erforderlich ist. Für wissenschaftliche Publikationen verwenden Sie bitte spezialisierte Software wie R mit dem `survey`-Paket, SAS oder SPSS mit den entsprechenden Survey-Modulen.

---

*cheatstat Version 4.1.2 | Letzte Aktualisierung: März 2026 | Autor: Jürgen Leibold | Lizenz: MIT*