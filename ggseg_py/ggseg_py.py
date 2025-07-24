import warnings
from collections.abc import Sequence

import geopandas as gpd
import pandas as pd
from rdata import read_rda
from shapely.geometry import MultiPolygon, Polygon


def _list_to_multipolygon(coords: list[Sequence[Sequence[float]]]) -> MultiPolygon:
    """
    Convert a nested list of rings into a MultiPolygon.

    Parameters
    ----------
    coords : sequence of polygons
        Each polygon is a sequence of rings, and each ring is a sequence of [x, y] floats.

    Returns
    -------
    MultiPolygon
        Combined geometry of all polygons.
    """
    polys: list[Polygon] = []
    for polygon in coords:
        if not polygon:
            continue
        exterior = polygon[0]
        interiors = polygon[1:] if len(polygon) > 1 else []
        polys.append(Polygon(shell=exterior, holes=interiors))
    return MultiPolygon(polys)


def rda2gpd(path2atlas: str, atlas_name: str) -> gpd.GeoDataFrame:
    """
    Load atlas data from an R .rda file and convert to GeoDataFrame.

    Parameters
    ----------
    path2atlas : str
        Filepath to the .rda atlas file.
    atlas_name : str
        Name of the object inside the .rda to extract (e.g., 'aseg').

    Returns
    -------
    GeoDataFrame
        A GeoDataFrame with 'geometry', 'region', 'label', and optional 'roi' columns.
    """
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')  # ignoring because fixing issues below
        atlas_r: dict = read_rda(path2atlas)
    df: pd.DataFrame = atlas_r[atlas_name]['data']  # type: ignore

    # Convert nested lists to MultiPolygon
    df['geometry'] = df['geometry'].apply(_list_to_multipolygon)

    # Clean up region and label fields
    regions: list[str] = []
    labels: list[str] = []
    for region, label in zip(df['region'], df['label']):
        regions.append(region if region is not None else '???')
        labels.append(label if label is not None else '???')
    df['region'] = regions
    df['label'] = labels

    # Add 'roi' column for aseg atlas
    if atlas_name == 'aseg':
        df['roi'] = df['hemi'] + '_' + df['label']  # type: ignore

    return gpd.GeoDataFrame(df, geometry='geometry')


def merge_data(data: pd.DataFrame, geo_df: gpd.GeoDataFrame, atlas_name: str) -> gpd.GeoDataFrame:
    """
    Merge external measurement data with atlas geometries.

    Parameters
    ----------
    data : DataFrame
        Table containing a 'StructName' column mapping to atlas ROIs.
    geo_df : GeoDataFrame
        GeoDataFrame produced by `rda2gpd`, including 'roi' column.
    atlas_name : str
        One of ['aseg', 'glasser', 'dk'], selects appropriate mapping dict.

    Returns
    -------
    GeoDataFrame
        Merged geospatial dataframe with measurements joined on 'roi'.
    """
    # Dynamically import the correct conversion dictionary
    if atlas_name == 'aseg':
        from ggseg_py.conversion_dicts import aseg_dict as mapping
    elif atlas_name == 'glasser':
        from ggseg_py.conversion_dicts import glasser_dict as mapping
    elif atlas_name == 'dk':
        from ggseg_py.conversion_dicts import dk_dict as mapping
    else:
        raise ValueError(f'Unsupported atlas_name: {atlas_name}')

    # Create ROI column in data
    data = data.copy()
    data['roi'] = data['StructName'].replace(mapping)  # type: ignore

    # Merge and return
    return geo_df.merge(data, on='roi', how='outer')
