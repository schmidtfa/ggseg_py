from typing import Any

import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Patch


def _prepare_coloring(
    data: pd.Series, cmap: str | mcolors.Colormap, vmin: float | None, vmax: float | None
) -> tuple[bool, Any, Any, mcolors.Colormap]:
    """
    Determine if data is numeric or categorical and compute the appropriate coloring mapping.

    If the data is numeric, returns a Normalize object for consistent scaling across plots.
    If the data is categorical, returns a mapping of category values to colors.

    Parameters
    ----------
    data : pd.Series
        Series of values to map to colors.
    cmap : str or Colormap
        Matplotlib colormap name or instance.
    vmin : float, optional
        Minimum data value for normalization (overrides data min).
    vmax : float, optional
        Maximum data value for normalization (overrides data max).

    Returns
    -------
    is_numeric : bool
        True if data is numeric, False if categorical.
    norm : Normalize or None
        Matplotlib Normalize (or TwoSlopeNorm) for numeric data.
    color_map : dict or None
        Mapping from category to RGBA color for categorical data.
    cmap : Colormap
        Resolved Matplotlib colormap instance.
    """
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)
    vals = data.dropna()
    is_numeric = pd.api.types.is_numeric_dtype(vals)
    norm: mcolors.Normalize | None = None
    color_map: dict | None = None
    if is_numeric:
        low = vmin if vmin is not None else vals.min()
        high = vmax if vmax is not None else vals.max()
        if low < 0 < high:
            lim = max(abs(low), abs(high))
            norm = TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim)
        else:
            norm = mcolors.Normalize(vmin=low, vmax=high)
    else:
        cats = pd.Categorical(vals).categories
        n = len(cats)
        colors = [cmap(i / max(n - 1, 1)) for i in range(n)]
        color_map = dict(zip(cats, colors))
    return is_numeric, norm, color_map, cmap


def _add_colorbar(
    fig: plt.Figure,
    axes: np.ndarray,
    label: str,
    cmap: mcolors.Colormap,
    norm: mcolors.Normalize | None = None,
    color_map: dict | None = None,
) -> None:
    """
    Attach a colorbar or categorical legend to the figure.

    Parameters
    ----------
    fig : Figure
        Matplotlib Figure containing the axes.
    axes : single Axes or array of Axes
        Axes the colorbar should relate to.
    label : str
        Title for the colorbar or legend.
    cmap : Colormap
        Colormap used for numeric data mapping.
    norm : Normalize, optional
        Normalize instance for numeric data; if provided, a colorbar is created.
    color_map : dict, optional
        Category-to-color mapping for categorical data; if provided, a legend is created.
    """
    if color_map is not None:
        patches = [Patch(facecolor=color_map[cat], edgecolor='black', label=str(cat)) for cat in color_map]
        fig.legend(handles=patches, title=label, loc='center left', bbox_to_anchor=(1.02, 0.5))
    elif norm is not None:
        mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
        cbar = fig.colorbar(mappable, ax=axes, orientation='vertical', fraction=0.05, pad=0.02)
        cbar.set_label(label)


def _plot_views(
    gdf: gpd.GeoDataFrame,
    views: list[dict],
    column: str,
    cmap: mcolors.Colormap,
    mask_region: str | None,
    edgecolor: str,
    linewidth: float,
    aspect: float,
    axes: np.ndarray,
    norm: mcolors.Normalize | None,
    color_map: dict | None,
) -> None:
    """
    Render a list of atlas views onto provided axes.

    Parameters
    ----------
    gdf : GeoDataFrame
        Input geospatial data with 'side', 'hemi', and specified column.
    views : list of dict
        Each dict must have 'side' and 'hemi' keys for filtering.
    column : str
        Column name to color by.
    cmap : Colormap
        Colormap for numeric plots or used to generate category colors.
    mask_region : str or None
        Region label to draw as gray mask on top of plots.
    edgecolor : str
        Color for polygon edges.
    linewidth : float
        Width of polygon edges.
    aspect : float
        Aspect ratio for each subplot.
    axes : array-like of Axes
        Axes objects corresponding to each view in 'views'.
    norm : Normalize or None
        Shared normalization for numeric data.
    color_map : dict or None
        Shared mapping from category to color.
    """
    for ax, view in zip(np.ravel(axes), views):
        sel = gdf[gdf['side'] == view['side']]
        hemi = view['hemi']
        sel = sel[sel['hemi'].isin(hemi)] if isinstance(hemi, list | tuple) else sel[sel['hemi'] == hemi]
        if norm is not None:
            sel.plot(
                column=column,
                cmap=cmap,
                norm=norm,
                edgecolor=edgecolor,
                linewidth=linewidth,
                aspect=aspect,
                legend=False,
                ax=ax,
            )
        elif color_map is not None:
            sel_colors = sel[column].map(color_map)
            sel.plot(color=sel_colors, edgecolor=edgecolor, linewidth=linewidth, aspect=aspect, ax=ax)
        if mask_region:
            mask = gdf[(gdf['side'] == view['side']) & (gdf.get('region') == mask_region)]
            mask.plot(color='#A1A1A1', edgecolor=edgecolor, linewidth=linewidth, aspect=aspect, ax=ax)
        ax.set_axis_off()


def _plot_multi(
    gdf: gpd.GeoDataFrame,
    views: list,
    layout: tuple[int, int],
    column: str,
    cmap: str | mcolors.Colormap,
    mask_region: str | None,
    edgecolor: str,
    linewidth: float,
    aspect: float,
    figsize: tuple[int, int],
    vmin: float | None,
    vmax: float | None,
    show_cbar: bool,
) -> tuple[plt.Figure, np.ndarray]:
    """
    Generic multi-panel plotting framework for atlas views.

    Parameters
    ----------
    gdf : GeoDataFrame
        Input geospatial data.
    views : list of dict
        View definitions with 'side' and 'hemi'.
    layout : tuple of ints
        (n_rows, n_cols) specifying subplot grid.
    column : str
        Column name to color by.
    cmap : str or Colormap
        Colormap for mapping data values.
    mask_region : str or None
        Region to mask in gray.
    edgecolor : str
        Edge color for polygons.
    linewidth : float
        Line width for polygon edges.
    aspect : float
        Aspect ratio for axes.
    figsize : tuple of ints
        Figure size (width, height).
    vmin : float or None
        Minimum data value for normalization.
    vmax : float or None
        Maximum data value for normalization.
    show_cbar : bool
        If True, display colorbar or legend.

    Returns
    -------
    fig : Figure
        Matplotlib Figure containing the axes.
    axes : array-like
        Array of Axes objects corresponding to each view.
    """
    is_num, norm, color_map, cmap = _prepare_coloring(gdf[column], cmap, vmin, vmax)
    fig, axes = plt.subplots(layout[0], layout[1], figsize=figsize, squeeze=False)
    _plot_views(gdf, views, column, cmap, mask_region, edgecolor, linewidth, aspect, axes, norm, color_map)
    if show_cbar:
        gdf[column]
        _add_colorbar(fig, axes, column, cmap, norm=norm, color_map=color_map)
    return fig, axes


def plot_aseg(
    gdf: gpd.GeoDataFrame,
    value: str = 'label',
    cmap: str | mcolors.Colormap = 'viridis',
    mask_region: str = '???',
    vmin: float | None = None,
    vmax: float | None = None,
    show_cbar: bool = True,
) -> tuple[plt.Figure, np.ndarray]:
    """
    Plot ASEG volumetric segmentation in coronal and sagittal views.

    Parameters
    ----------
    gdf : GeoDataFrame
        ASEG atlas geodata with 'side', 'hemi', 'region', and measurement columns.
    value : str
        Column name containing the data to visualize.
    cmap : str or Colormap
        Colormap for mapping values or categories.
    mask_region : str
        Region label to overlay as gray mask.
    vmin : float, optional
        Lower bound for colormap normalization.
    vmax : float, optional
        Upper bound for colormap normalization.
    show_cbar : bool, default True
        If True, display a colorbar (numeric) or legend (categorical).

    Returns
    -------
    fig : Figure
        Matplotlib Figure with two subplots (coronal, sagittal).
    axes : array-like
        Axes for the respective views: [0]=coronal, [1]=sagittal.
    """
    views = [{'side': 'coronal', 'hemi': ['left', 'right']}, {'side': 'sagittal', 'hemi': 'midline'}]
    return _plot_multi(gdf, views, (1, 2), value, cmap, mask_region, 'black', 1.0, 1, (10, 5), vmin, vmax, show_cbar)


def plot_surface(
    gdf: gpd.GeoDataFrame,
    column: str = 'label',
    cmap: str | mcolors.Colormap = 'tab20',
    edgecolor: str = 'black',
    linewidth: float = 1.5,
    figsize: tuple[int, int] = (7, 5),
    aspect: float = 1,
    vmin: float | None = None,
    vmax: float | None = None,
    show_cbar: bool = False,
) -> tuple[plt.Figure, np.ndarray]:
    """
    Plot surface atlas in lateral and medial views for both hemispheres.

    Parameters
    ----------
    gdf : GeoDataFrame
        Surface atlas geodata with 'side', 'hemi', and data column.
    column : str
        Column name containing labels or measurements.
    cmap : str or Colormap
        Colormap for mapping values or categories.
    edgecolor : str
        Color of polygon edges.
    linewidth : float
        Width of polygon edges.
    figsize : tuple
        Figure size (width, height) in inches.
    aspect : float
        Aspect ratio for each subplot.
    vmin : float, optional
        Lower bound for numeric colormap.
    vmax : float, optional
        Upper bound for numeric colormap.
    show_cbar : bool, default False
        If True, display a colorbar or legend.

    Returns
    -------
    fig : Figure
        Matplotlib Figure with 2x2 subplots (lateral L/R, medial L/R).
    axes : array-like
        Array of Axes in layout [[lat L, lat R], [med L, med R]].
    """
    views = [
        {'side': 'lateral', 'hemi': 'left'},
        {'side': 'lateral', 'hemi': 'right'},
        {'side': 'medial', 'hemi': 'left'},
        {'side': 'medial', 'hemi': 'right'},
    ]
    return _plot_multi(
        gdf, views, (2, 2), column, cmap, None, edgecolor, linewidth, aspect, figsize, vmin, vmax, show_cbar
    )


def plot_view(
    gdf: gpd.GeoDataFrame,
    side: str,
    hemi: str,
    column: str = 'label',
    cmap: str | mcolors.Colormap = 'viridis',
    edgecolor: str = 'black',
    linewidth: float = 1.5,
    figsize: tuple[int, int] = (5, 5),
    aspect: float = 1,
    vmin: float | None = None,
    vmax: float | None = None,
    show_cbar: bool = False,
) -> tuple[plt.Figure, plt.Axes]:
    """
    Plot a single hemisphere/side view of an atlas.

    Parameters
    ----------
    gdf : GeoDataFrame
        Atlas geodata with 'side', 'hemi', and specified data column.
    side : str
        View orientation (e.g., 'lateral', 'medial', 'coronal', 'sagittal').
    hemi : str
        Hemisphere identifier ('left', 'right', or 'midline').
    column : str
        Column name for values or labels to plot.
    cmap : str or Colormap
        Colormap for numeric or categorical data.
    edgecolor : str
        Color for polygon edges.
    linewidth : float
        Width of polygon edges.
    figsize : tuple
        Figure size (width, height).
    aspect : float
        Aspect ratio of the plot.
    vmin : float, optional
        Lower bound for numeric colormap.
    vmax : float, optional
        Upper bound for numeric colormap.
    show_cbar : bool
        If True, display a colorbar or legend.

    Returns
    -------
    fig : Figure
        Matplotlib Figure containing the single subplot.
    ax : Axes
        Matplotlib Axes for the request view.
    """
    views = [{'side': side, 'hemi': hemi}]
    fig, axes = _plot_multi(
        gdf, views, (1, 1), column, cmap, None, edgecolor, linewidth, aspect, figsize, vmin, vmax, show_cbar
    )
    return fig, axes[0, 0]
