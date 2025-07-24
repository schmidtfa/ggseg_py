## Welcome to ggseg_py

[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-green.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Coverage Status](https://coveralls.io/repos/github/schmidtfa/ggseg_py/badge.svg?branch=main)](https://coveralls.io/github/schmidtfa/ggseg_py?branch=main)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


ggseg_py is a python adaptation of the famous [ggseg](https://github.com/ggseg) R package. ggseg_py facilitates 2D brain plots by making heavy use of geopandas and matplotlib. 

In a nutshell: ggseg based .rda files containing multipolygons for different brain regions are used when creating geopandas dataframes. These dataframes can be easily merged with normal pandas dataframes containing the data you want to plot for a given ROI.
The package also contains some convenience functions to plot these dataframes using matplotlib.

This package is merely a wrapper around the efforts made by the smart people that developed ggseg and when you use this set of functions to visualize some brains you should also cite them :)

Mowinckel, A. M., & Vidal-Piñeiro, D. (2020). Visualization of brain statistics with R packages ggseg and ggseg3d. Advances in Methods and Practices in Psychological Science, 3(4), 466-483.

If you like ggseg_py please drop a star to support me :)

```
[pypi-dependencies]
ggseg_py = { git = "https://github.com/schmidtfa/ggseg_py.git"}
```

or use pip

```
pip install "git+https://github.com/schmidtfa/ggseg_py.git"
```