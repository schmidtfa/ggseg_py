import warnings
from collections.abc import Sequence

import geopandas as gpd
import pandas as pd
from rdata import read_rda
from shapely.geometry import MultiPolygon, Polygon
import os


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


def rda2gpd(atlas: str | os.PathLike) -> gpd.GeoDataFrame:
    """
    Load atlas data from an R .rda file and convert to GeoDataFrame.

    Parameters
    ----------
    atlas : str
        Name of an atlas or filepath to an .rda atlas file. 
        When using a "custom" rda file be aware that the object inside the .rda to extract data (e.g., 'aseg').
        should be labeled according to the atlas itself.

    Returns
    -------
    GeoDataFrame
        A GeoDataFrame with 'geometry', 'region', 'label', and optional 'roi' columns.
    """

    atlas_split = str(atlas).split('/')

    if len(atlas_split) == 1: 
        atlas_name = atlas_split[0]
        from pathlib import Path
        HERE = Path(__file__).parent.parent  
        if atlas_name == 'aseg':
            path2atlas = HERE / 'ggseg_py'/ 'atlases' / 'aseg.rda'
        elif atlas_name == 'glasser':
            path2atlas = HERE / 'ggseg_py' / 'atlases' / 'glasser.rda'
        elif atlas_name == 'dk':
            path2atlas = HERE / 'ggseg_py'/ 'atlases'/ 'dk.rda'
        else:
            raise ValueError('Currently only aseg, glasser and dk atlasses are supported directly. ' \
            'If you want to use a different ggseg compatible atlas taken from an rda file you need' \
            'to directly supply the path to said file.')
    else:
        path2atlas = atlas
        atlas_name = atlas_split[-1].split('.')[0]


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
    elif atlas_name == 'glasser':
        df['roi'] = [label.split('_')[1] + '_' + label.split('_')[-1] + '_ROI' for label in df['label']]

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

        # Create ROI column in data
        data = data.copy()
        data['roi'] = data['StructName'].replace(mapping)  # type: ignore
    else:
        raise ValueError(f'Unsupported atlas_name: {atlas_name}')

    # Merge and return
    return geo_df.merge(data, on='roi', how='outer')
