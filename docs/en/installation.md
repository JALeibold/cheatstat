# Installation

[← Back to Overview](index.md) | [🇩🇪 Deutsch](../de/installation.md)

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Installation via pip](#2-installation-via-pip)
3. [Installation via conda](#3-installation-via-conda)
4. [Dependencies](#4-dependencies)
5. [Verifying the Installation](#5-verifying-the-installation)
6. [Recommended Development Environments](#6-recommended-development-environments)
7. [Common Installation Issues](#7-common-installation-issues)
8. [Uninstalling](#8-uninstalling)

---

## 1. System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8 | 3.10+ |
| Operating System | Windows 10 / macOS 10.15 / Linux | any |
| RAM | 2 GB | 8 GB+ |
| Disk Space | 500 MB | 2 GB+ |

---

## 2. Installation via pip

### Basic Installation

```bash
pip install simplestat
```

### Full Installation (recommended)

For full functionality, additional packages are required:

```bash
pip install simplestat statsmodels
```

### Installation with All Optional Dependencies

```bash
pip install simplestat statsmodels numba openpyxl pyreadstat
```

### Install a Specific Version

```bash
pip install simplestat==4.0.0
```

### Upgrade to the Latest Version

```bash
pip install --upgrade simplestat
```

---

## 3. Installation via conda

### Via conda-forge (recommended)

```bash
conda install -c conda-forge simplestat
```

### Create a conda environment and install

```bash
# Create new environment
conda create -n sowi_stats python=3.10

# Activate environment
conda activate sowi_stats

# Install simpleStat and dependencies
conda install -c conda-forge simplestat statsmodels numba
```

---

## 4. Dependencies

### Required Dependencies

These packages are automatically installed with simpleStat:

| Package | Version | Usage |
|---------|---------|-------|
| `pandas` | ≥ 1.3.0 | Data processing |
| `numpy` | ≥ 1.20.0 | Numerical calculations |
| `scipy` | ≥ 1.7.0 | Statistical tests |

### Optional Dependencies

These packages extend functionality:

| Package | Installation | Required for |
|---------|-------------|-------------|
| `statsmodels` | `pip install statsmodels` | `regress()` – OLS regression |
| `numba` | `pip install numba` | Faster concordance calculations in `biV()` |
| `openpyxl` | `pip install openpyxl` | `export_results(..., format='excel')` |
| `pyreadstat` | `pip install pyreadstat` | Loading SPSS files (`.sav`) |

> **Note:** Without `statsmodels`, the `regress()` function is not available.
> Without `numba`, a Python fallback is used, which is slower for large datasets.

### Install all optional dependencies at once

```bash
pip install simplestat[full]
```

---

## 5. Verifying the Installation

### Basic Check

```python
import simpleStat as sis
print("simpleStat successfully loaded!")
sis.help_simpleStat()
```

### Full Check with Test Data

```python
import simpleStat as sis
import pandas as pd
import numpy as np

# Create test data
np.random.seed(42)
df = pd.DataFrame({
    'sex': np.random.choice([1.0, 2.0], 100),
    'inc': np.random.normal(2000, 500, 100),
    'educ': np.random.choice([1, 2, 3], 100)
})

# Test functions
print("=== Test: fre() ===")
print(sis.fre(df['sex']))

print("\n=== Test: uniV() ===")
sis.uniV(df, 'inc').summary()

print("\n=== Test: ttest_u() ===")
sis.ttest_u(group='sex', g1=1.0, g2=2.0,
            dependent='inc', data=df).summary()

print("\n✅ All tests passed!")
```

### Check Availability of Optional Packages

```python
# statsmodels
try:
    import statsmodels
    print(f"✅ statsmodels {statsmodels.__version__} available")
except ImportError:
    print("❌ statsmodels not installed → regress() not available")

# numba
try:
    import numba
    print(f"✅ numba {numba.__version__} available → fast calculations")
except ImportError:
    print("⚠️  numba not installed → Python fallback will be used")

# openpyxl
try:
    import openpyxl
    print(f"✅ openpyxl {openpyxl.__version__} available → Excel export possible")
except ImportError:
    print("❌ openpyxl not installed → no Excel export")

# pyreadstat
try:
    import pyreadstat
    print(f"✅ pyreadstat available → SPSS files can be loaded")
except ImportError:
    print("❌ pyreadstat not installed → SPSS files cannot be loaded")
```

---

## 6. Recommended Development Environments

### Jupyter Notebook / JupyterLab (recommended for beginners)

```bash
pip install jupyter
jupyter notebook
```

Create a new notebook and start with:

```python
import simpleStat as sis
import pandas as pd
import numpy as np
```

### Spyder (for SPSS/Stata users)

Spyder offers an SPSS-like interface with variable explorer:

```bash
pip install spyder
spyder
```

### VS Code

1. Install VS Code: [code.visualstudio.com](https://code.visualstudio.com)
2. Install the Python extension
3. Install the Jupyter extension

### PyCharm

1. Download PyCharm Community Edition (free)
2. Create a new Python project
3. Install simpleStat via the built-in package manager

---

## 7. Common Installation Issues

### Issue: `ModuleNotFoundError: No module named 'simpleStat'`

**Cause:** simpleStat is installed in the wrong Python environment.

```bash
# Check which Python version is being used
python --version
which python    # macOS/Linux
where python    # Windows

# Ensure pip uses the correct Python version
python -m pip install simplestat
```

### Issue: `pip: command not found`

```bash
# Explicitly specify Python 3
python3 -m pip install simplestat
```

### Issue: `PermissionError` during installation

```bash
# Install for current user only
pip install --user simplestat
```

### Issue: Conflicts with existing packages

```bash
# Create a virtual environment
python -m venv sowi_env
source sowi_env/bin/activate    # macOS/Linux
sowi_env\Scripts\activate       # Windows

pip install simplestat statsmodels
```

### Issue: `ImportError: statsmodels not installed`

When `regress()` is called without statsmodels installed:

```bash
pip install statsmodels
```

### Issue: Slow calculations in `biV()`

Install numba for JIT-compiled concordance calculations:

```bash
pip install numba
```

---

## 8. Uninstalling

```bash
pip uninstall simplestat
```

To remove all dependencies:

```bash
pip uninstall simplestat statsmodels numba openpyxl pyreadstat
```

---

*simpleStat Version 4.0 | Author: Jürgen Leibold | March 2026*

[→ Next: Basic Usage](usage.md) | [← Back to Overview](index.md)

# Installation

[← Back to Overview](index.md) | [🇩🇪 Deutsch](../de/installation.md)

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Installation via pip](#2-installation-via-pip)
3. [Installation via conda](#3-installation-via-conda)
4. [Dependencies](#4-dependencies)
5. [Verifying the Installation](#5-verifying-the-installation)
6. [Recommended Development Environments](#6-recommended-development-environments)
7. [Common Installation Issues](#7-common-installation-issues)
8. [Uninstalling](#8-uninstalling)

---

## 1. System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8 | 3.10+ |
| Operating System | Windows 10 / macOS 10.15 / Linux | any |
| RAM | 2 GB | 8 GB+ |
| Disk Space | 500 MB | 2 GB+ |

---

## 2. Installation via pip

### Basic Installation

```bash
pip install cheatstat
```

### Full Installation (recommended)

For full functionality, additional packages are required:

```bash
pip install cheatstat statsmodels
```

### Installation with All Optional Dependencies

```bash
pip install cheatstat statsmodels numba openpyxl pyreadstat
```

### Install a Specific Version

```bash
pip install cheatstat==4.1.0
```

### Upgrade to the Latest Version

```bash
pip install --upgrade cheatstat
```

---

## 3. Installation via conda

### Via conda-forge (recommended)

```bash
conda install -c conda-forge cheatstat
```

### Create a conda environment and install

```bash
# Create new environment
conda create -n sowi_stats python=3.10

# Activate environment
conda activate sowi_stats

# Install cheatstat and dependencies
conda install -c conda-forge cheatstat statsmodels numba
```

---

## 4. Dependencies

### Required Dependencies

These packages are automatically installed with cheatstat:

| Package | Version | Usage |
|---------|---------|-------|
| `pandas` | ≥ 1.3.0 | Data processing |
| `numpy` | ≥ 1.20.0 | Numerical calculations |
| `scipy` | ≥ 1.7.0 | Statistical tests |

### Optional Dependencies

These packages extend functionality:

| Package | Installation | Required for |
|---------|-------------|-------------|
| `statsmodels` | `pip install statsmodels` | `regress()` – OLS regression |
| `numba` | `pip install numba` | Faster concordance calculations in `biV()` |
| `openpyxl` | `pip install openpyxl` | `export_results(..., format='excel')` |
| `pyreadstat` | `pip install pyreadstat` | Loading SPSS files (`.sav`) |

> **Note:** Without `statsmodels`, the `regress()` function is not available.
> Without `numba`, a Python fallback is used, which is slower for large datasets.

### Install all optional dependencies at once

```bash
pip install cheatstat[full]
```

---

## 5. Verifying the Installation

### Basic Check

```python
import cheatstat as cs
print("cheatstat successfully loaded!")
cs.help_cheatstat()
```

### Full Check with Test Data

```python
import cheatstat as cs
import pandas as pd
import numpy as np

# Create test data
np.random.seed(42)
df = pd.DataFrame({
    'sex': np.random.choice([1.0, 2.0], 100),
    'inc': np.random.normal(2000, 500, 100),
    'educ': np.random.choice([1, 2, 3], 100)
})

# Test functions
print("=== Test: fre() ===")
print(cs.fre(df, 'sex'))

print("\n=== Test: uniV() ===")
cs.uniV(df, 'inc').summary()

print("\n=== Test: ttest_u() ===")
cs.ttest_u(group='sex', g1=1.0, g2=2.0,
           dependent='inc', data=df).summary()

print("\n✅ All tests passed!")
```

### Check Availability of Optional Packages

```python
# statsmodels
try:
    import statsmodels
    print(f"✅ statsmodels {statsmodels.__version__} available")
except ImportError:
    print("❌ statsmodels not installed → regress() not available")

# numba
try:
    import numba
    print(f"✅ numba {numba.__version__} available → fast calculations")
except ImportError:
    print("⚠️  numba not installed → Python fallback will be used")

# openpyxl
try:
    import openpyxl
    print(f"✅ openpyxl {openpyxl.__version__} available → Excel export possible")
except ImportError:
    print("❌ openpyxl not installed → no Excel export")

# pyreadstat
try:
    import pyreadstat
    print(f"✅ pyreadstat available → SPSS files can be loaded")
except ImportError:
    print("❌ pyreadstat not installed → SPSS files cannot be loaded")
```

---

## 6. Recommended Development Environments

### Jupyter Notebook / JupyterLab (recommended for beginners)

```bash
pip install jupyter
jupyter notebook
```

Create a new notebook and start with:

```python
import cheatstat as cs
import pandas as pd
import numpy as np
```

### Spyder (for SPSS/Stata users)

Spyder offers an SPSS-like interface with variable explorer:

```bash
pip install spyder
spyder
```

### VS Code

1. Install VS Code: [code.visualstudio.com](https://code.visualstudio.com)
2. Install the Python extension
3. Install the Jupyter extension

### PyCharm

1. Download PyCharm Community Edition (free)
2. Create a new Python project
3. Install cheatstat via the built-in package manager

---

## 7. Common Installation Issues

### Issue: `ModuleNotFoundError: No module named 'cheatstat'`

**Cause:** cheatstat is installed in the wrong Python environment.

```bash
# Check which Python version is being used
python --version
which python    # macOS/Linux
where python    # Windows

# Ensure pip uses the correct Python version
python -m pip install cheatstat
```

### Issue: `pip: command not found`

```bash
# Explicitly specify Python 3
python3 -m pip install cheatstat
```

### Issue: `PermissionError` during installation

```bash
# Install for current user only
pip install --user cheatstat
```

### Issue: Conflicts with existing packages

```bash
# Create a virtual environment
python -m venv sowi_env
source sowi_env/bin/activate    # macOS/Linux
sowi_env\Scripts\activate       # Windows

pip install cheatstat statsmodels
```

### Issue: `ImportError: statsmodels not installed`

When `regress()` is called without statsmodels installed:

```bash
pip install statsmodels
```

### Issue: Slow calculations in `biV()`

Install numba for JIT-compiled concordance calculations:

```bash
pip install numba
```

---

## 8. Uninstalling

```bash
pip uninstall cheatstat
```

To remove all dependencies:

```bash
pip uninstall cheatstat statsmodels numba openpyxl pyreadstat
```

---

*cheatstat Version 4.1 | Author: Jürgen Leibold | March 2026*

[→ Next: Basic Usage](usage.md) | [← Back to Overview](index.md)

