## Welcome to ggseg_py

[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-green.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Coverage Status](https://coveralls.io/repos/github/schmidtfa/ggseg_py/badge.svg?branch=main)](https://coveralls.io/github/schmidtfa/ggseg_py?branch=main)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


ggseg_py is a python adaptation of the famous [ggseg](https://github.com/ggseg) R package. ggseg_py facilitates 2D brain plots by making heavy use of geopandas and matplotlib. In a nutshell: ggseg based .rda files containing MULTIPOLYGONS for different brain regions are used to create geopandas dataframes. These dataframes can be easily merged with normal pandas dataframes containing your data for a given ROI.
The package also contains some convenience functions to plot these dataframes using matplotlib.


```
[pypi-dependencies]
ggseg_py = { git = "https://github.com/schmidtfa/ggseg_py.git"}
```

or use pip

```
pip install "git+https://github.com/schmidtfa/ggseg_py.git"
```