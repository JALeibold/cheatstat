# Installation

[← Zurück zur Übersicht](index.md) | [🇬🇧 English](../en/installation.md)

---

## Inhaltsverzeichnis

1. [Systemvoraussetzungen](#1-systemvoraussetzungen)
2. [Installation über pip](#2-installation-über-pip)
3. [Installation über conda](#3-installation-über-conda)
4. [Abhängigkeiten](#4-abhängigkeiten)
5. [Installation überprüfen](#5-installation-überprüfen)
6. [Empfohlene Entwicklungsumgebungen](#6-empfohlene-entwicklungsumgebungen)
7. [Häufige Installationsprobleme](#7-häufige-installationsprobleme)
8. [Deinstallation](#8-deinstallation)

---

## 1. Systemvoraussetzungen

| Anforderung | Minimum | Empfohlen |
|-------------|---------|-----------|
| Python | 3.8 | 3.10+ |
| Betriebssystem | Windows 10 / macOS 10.15 / Linux | beliebig |
| RAM | 2 GB | 8 GB+ |
| Festplattenspeicher | 500 MB | 2 GB+ |

---

## 2. Installation über pip

### Basisinstallation

```bash
pip install cheatstat
```

### Vollständige Installation (empfohlen)

Für die vollständige Funktionalität werden zusätzliche Pakete benötigt:

```bash
pip install cheatstat statsmodels
```

### Installation mit allen optionalen Abhängigkeiten

```bash
pip install cheatstat statsmodels numba openpyxl pyreadstat
```

### Spezifische Version installieren

```bash
pip install cheatstat==4.1.0
```

### Upgrade auf die neueste Version

```bash
pip install --upgrade cheatstat
```

---

## 3. Installation über conda

### Über conda-forge (empfohlen)

```bash
conda install -c conda-forge cheatstat
```

### Conda-Umgebung erstellen und installieren

```bash
# Neue Umgebung erstellen
conda create -n sowi_stats python=3.10

# Umgebung aktivieren
conda activate sowi_stats

# cheatstat und Abhängigkeiten installieren
conda install -c conda-forge cheatstat statsmodels numba
```

---

## 4. Abhängigkeiten

### Pflichtige Abhängigkeiten

Diese Pakete werden automatisch mit cheatstat installiert:

| Paket | Version | Verwendung |
|-------|---------|-----------|
| `pandas` | ≥ 1.3.0 | Datenverarbeitung |
| `numpy` | ≥ 1.20.0 | Numerische Berechnungen |
| `scipy` | ≥ 1.7.0 | Statistische Tests |

### Optionale Abhängigkeiten

Diese Pakete erweitern die Funktionalität:

| Paket | Installation | Wofür benötigt |
|-------|-------------|----------------|
| `statsmodels` | `pip install statsmodels` | `regress()` – OLS-Regression |
| `numba` | `pip install numba` | Schnellere Konkordanzberechnungen bei `biV()` |
| `openpyxl` | `pip install openpyxl` | `export_results(..., format='excel')` |
| `pyreadstat` | `pip install pyreadstat` | SPSS-Dateien laden (`.sav`) |

> **Hinweis:** Ohne `statsmodels` ist die Funktion `regress()` nicht
> verfügbar. Ohne `numba` wird ein Python-Fallback verwendet, der bei
> großen Datensätzen langsamer ist.

### Alle optionalen Abhängigkeiten auf einmal installieren

```bash
pip install cheatstat[full]
```

---

## 5. Installation überprüfen

### Grundlegende Prüfung

```python
import cheatstat as cs
print("cheatstat erfolgreich geladen!")
cs.help_cheatstat()
```

### Vollständige Prüfung mit Testdaten

```python
import cheatstat as cs
import pandas as pd
import numpy as np

# Testdaten erstellen
np.random.seed(42)
df = pd.DataFrame({
    'sex': np.random.choice([1.0, 2.0], 100),
    'inc': np.random.normal(2000, 500, 100),
    'educ': np.random.choice([1, 2, 3], 100)
})

# Funktionen testen
print("=== Test: fre() ===")
print(cs.fre(df, 'sex'))

print("\n=== Test: uniV() ===")
cs.uniV(df, 'inc').summary()

print("\n=== Test: ttest_u() ===")
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=df).summary()

print("\n✅ Alle Tests bestanden!")
```

### Verfügbarkeit optionaler Pakete prüfen

```python
# statsmodels
try:
    import statsmodels
    print(f"✅ statsmodels {statsmodels.__version__} verfügbar")
except ImportError:
    print("❌ statsmodels nicht installiert → regress() nicht verfügbar")

# numba
try:
    import numba
    print(f"✅ numba {numba.__version__} verfügbar → schnelle Berechnungen")
except ImportError:
    print("⚠️  numba nicht installiert → Python-Fallback wird verwendet")

# openpyxl
try:
    import openpyxl
    print(f"✅ openpyxl {openpyxl.__version__} verfügbar → Excel-Export möglich")
except ImportError:
    print("❌ openpyxl nicht installiert → kein Excel-Export")

# pyreadstat
try:
    import pyreadstat
    print(f"✅ pyreadstat verfügbar → SPSS-Dateien ladbar")
except ImportError:
    print("❌ pyreadstat nicht installiert → SPSS-Dateien nicht ladbar")
```

---

## 6. Empfohlene Entwicklungsumgebungen

### Jupyter Notebook / JupyterLab (empfohlen für Einsteiger)

```bash
pip install jupyter
jupyter notebook
```

Erstellen Sie ein neues Notebook und beginnen Sie mit:

```python
import cheatstat as cs
import pandas as pd
import numpy as np
```

### Spyder (für SPSS-/Stata-Umsteiger)

Spyder bietet eine SPSS-ähnliche Oberfläche mit Variablenexplorer:

```bash
pip install spyder
spyder
```

### VS Code

1. VS Code installieren: [code.visualstudio.com](https://code.visualstudio.com)
2. Python-Extension installieren
3. Jupyter-Extension installieren

### PyCharm

1. PyCharm Community Edition herunterladen (kostenlos)
2. Neues Python-Projekt erstellen
3. cheatstat über den integrierten Paketmanager installieren

---

## 7. Häufige Installationsprobleme

### Problem: `ModuleNotFoundError: No module named 'cheatstat'`

**Ursache:** cheatstat ist in der falschen Python-Umgebung installiert.

```bash
# Überprüfen, welche Python-Version verwendet wird
python --version
which python    # macOS/Linux
where python    # Windows

# Sicherstellen, dass pip die richtige Python-Version verwendet
python -m pip install cheatstat
```

### Problem: `pip: command not found`

```bash
# Python 3 explizit angeben
python3 -m pip install cheatstat
```

### Problem: `PermissionError` bei der Installation

```bash
# Installation für den aktuellen Benutzer
pip install --user cheatstat
```

### Problem: Konflikte mit bestehenden Paketen

```bash
# Virtuelle Umgebung erstellen
python -m venv sowi_env
source sowi_env/bin/activate    # macOS/Linux
sowi_env\Scripts\activate       # Windows

pip install cheatstat statsmodels
```

### Problem: `ImportError: statsmodels not installed`

Wenn `regress()` aufgerufen wird, ohne dass statsmodels installiert ist:

```bash
pip install statsmodels
```

### Problem: Langsame Berechnungen bei `biV()`

Installieren Sie numba für JIT-kompilierte Konkordanzberechnungen:

```bash
pip install numba
```

---

## 8. Deinstallation

```bash
pip uninstall cheatstat
```

Um alle Abhängigkeiten zu entfernen:

```bash
pip uninstall cheatstat statsmodels numba openpyxl pyreadstat
```

---

*cheatstat Version 4.1.2 | Autor: Jürgen Leibold | März 2026*

[→ Nächste Seite: Grundlegende Nutzung](usage.md) | [← Zurück zur Übersicht](index.md)