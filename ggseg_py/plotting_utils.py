import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import cm
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Patch


def _add_colorbar(fig, axes, data, cmap, label):
    """
    Add a shared vertical colorbar to the figure for the given data and colormap.
    If `data` is non-numeric (e.g., strings or categorical), create a legend instead.
    """
    # Drop NaNs
    data_vals = data.dropna()

    # Handle categorical/string data by legend
    if not pd.api.types.is_numeric_dtype(data_vals):
        categories = pd.Categorical(data_vals).categories
        # Generate distinct colors
        n = len(categories)
        colors = [cmap(i / max(n - 1, 1)) for i in range(n)]
        # Create legend patches
        patches = [Patch(facecolor=colors[i], edgecolor='black', label=str(cat)) for i, cat in enumerate(categories)]
        # Place legend to the right of axes
        fig.legend(handles=patches, title=label, loc='center left', bbox_to_anchor=(1.02, 0.5))
        return

    # Numeric data: colorbar
    vmin, vmax = data_vals.min(), data_vals.max()
    # Diverging norm if data spans zero
    if vmin < 0 < vmax:
        lim = max(abs(vmin), abs(vmax))
        norm = TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim)
    else:
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(mappable, ax=axes, orientation='vertical', fraction=0.05, pad=0.02)
    cbar.set_label(label)


def plot_aseg(aseg_data, value: str = 'label', cmap='tab20', mask_region: str = '???', show_cbar: bool = True):
    """
    Plot ASEG data in ggseg-style coronal and sagittal views.

    Parameters
    ----------
    aseg_data : GeoDataFrame
        Geospatial data with columns ['side', 'hemi', 'region', <value>].
    value : str
        Column name in `aseg_data` to color by.
    cmap : str or Colormap
        Matplotlib colormap name or Colormap instance.
    mask_region : str
        Name of region to draw in gray as background mask.
    show_cbar : bool
        Whether to display a colorbar.
    """
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    views = [{'side': 'coronal', 'hemi': ['left', 'right']}, {'side': 'sagittal', 'hemi': 'midline'}]
    for ax, view in zip(axes, views):
        sel = aseg_data[aseg_data['side'] == view['side']]
        if isinstance(view['hemi'], list | tuple):
            sel = sel[sel['hemi'].isin(view['hemi'])]
        else:
            sel = sel[sel['hemi'] == view['hemi']]
        sel.plot(column=value, cmap=cmap, legend=False, edgecolor='black', aspect=1, ax=ax)
        mask = aseg_data[(aseg_data['side'] == view['side']) & (aseg_data['region'] == mask_region)]
        mask.plot(color='#A1A1A1', edgecolor='black', aspect=1, ax=ax)
        ax.set_axis_off()
    if show_cbar:
        _add_colorbar(fig, axes, aseg_data[value], cmap, value)
    return fig, axes


def plot_surface(
    gdf,
    column: str = 'label',
    cmap='tab20',
    edgecolor: str = 'black',
    linewidth: float = 1.5,
    figsize: tuple = (7, 5),
    aspect: float = 1,
    show_cbar: bool = True,
):
    """
    Plot a surface-based model in lateral and medial views for both hemispheres.

    Parameters
    ----------
    gdf : GeoDataFrame
        Data with columns ['side', 'hemi', <column>].
    column : str
        Column name to color by.
    cmap : str or Colormap
        Matplotlib colormap name or Colormap instance to apply to all panels.
    edgecolor : str
        Color for polygon edges.
    linewidth : float
        Width of polygon edges.
    figsize : tuple
        Figure size for the plot.
    aspect : float
        Aspect ratio for each axis.
    show_cbar : bool
        Whether to display a colorbar.
    """
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)

    fig, axes = plt.subplots(2, 2, figsize=figsize)
    positions = [
        ('lateral', 'left', (0, 0)),
        ('lateral', 'right', (0, 1)),
        ('medial', 'left', (1, 0)),
        ('medial', 'right', (1, 1)),
    ]
    for side, hemi, (i, j) in positions:
        ax = axes[i, j]
        sel = gdf[(gdf['side'] == side) & (gdf['hemi'] == hemi)]
        sel.plot(column=column, cmap=cmap, legend=False, edgecolor=edgecolor, linewidth=linewidth, aspect=aspect, ax=ax)
        ax.set_axis_off()
    if show_cbar:
        _add_colorbar(fig, axes, gdf[column], cmap, column)
    return fig, axes


def plot_view(
    gdf,
    side: str,
    hemi: str,
    column: str = 'label',
    cmap='tab20',
    edgecolor: str = 'black',
    linewidth: float = 1.5,
    figsize: tuple = (5, 5),
    aspect: float = 1,
    show_cbar: bool = True,
):
    """
    Plot a single hemisphere/side view on its own axis.

    Parameters
    ----------
    gdf : GeoDataFrame
        Data with columns ['side', 'hemi', <column>].
    side : str
        One of ['lateral', 'medial', 'coronal', 'sagittal'].
    hemi : str
        Hemisphere identifier, e.g. 'left', 'right', or 'midline'.
    column : str
        Column name to color by.
    cmap : str or Colormap
        Matplotlib colormap name or Colormap instance.
    edgecolor : str
        Color for polygon edges.
    linewidth : float
        Width of polygon edges.
    figsize : tuple
        Figure size for the plot.
    aspect : float
        Aspect ratio for the axis.
    show_cbar : bool
        Whether to display a colorbar.

    Returns
    -------
    fig : matplotlib.figure.Figure
    ax : matplotlib.axes.Axes
    """
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)

    # Create single axis
    fig, ax = plt.subplots(figsize=figsize)

    # Select data for the requested side and hemisphere
    sel = gdf[(gdf['side'] == side) & (gdf['hemi'] == hemi)]
    # Plot
    sel.plot(column=column, cmap=cmap, legend=False, edgecolor=edgecolor, linewidth=linewidth, aspect=aspect, ax=ax)
    ax.set_axis_off()

    # Add colorbar if requested
    if show_cbar:
        _add_colorbar(fig, ax, sel[column], cmap, column)

    return fig, ax
