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
    Determine if data is numeric or categorical, compute normalization or color mapping.
    Returns is_numeric, Normalize or None, color_map or None, and resolved cmap.
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
    Add a colorbar for numeric data or legend for categorical.
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
    Render each view onto the corresponding axes.
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
    Generic multi-panel plotting for specified views and layout.
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
    Plot ASEG data in coronal+sagittal (1x2) layout.
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
    Plot lateral+medial surface (2x2) layout.
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
    Plot a single view (1x1) layout.
    """
    views = [{'side': side, 'hemi': hemi}]
    fig, axes = _plot_multi(
        gdf, views, (1, 1), column, cmap, None, edgecolor, linewidth, aspect, figsize, vmin, vmax, show_cbar
    )
    return fig, axes[0, 0]
