import warnings
from collections.abc import Sequence
from pathlib import Path

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


def rda2gpd(atlas: Path, return_atlas_fname: bool = False) -> gpd.GeoDataFrame:
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

        atlas_loc = Path(__file__).parent.parent
        if atlas_name == 'aseg':
            path2atlas = atlas_loc / 'ggseg_py' / 'atlases' / 'aseg.rda'
        elif atlas_name == 'glasser':
            path2atlas = atlas_loc / 'ggseg_py' / 'atlases' / 'glasser.rda'
        elif atlas_name == 'dk':
            path2atlas = atlas_loc / 'ggseg_py' / 'atlases' / 'dk.rda'
        else:
            raise ValueError(
                'Currently only aseg, glasser and dk atlasses are supported directly. '
                'If you want to use a different ggseg compatible atlas taken from an rda file you need'
                'to directly supply the path to said file.'
            )
    else:
        path2atlas = atlas
        atlas_name = atlas_split[-1].split('.')[0]

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')  # ignoring because fixing issues below
        atlas_r: dict = read_rda(path2atlas)
    df_atlas: pd.DataFrame = atlas_r[atlas_name]['data']  # type: ignore

    # Convert nested lists to MultiPolygon
    df_atlas['geometry'] = df_atlas['geometry'].apply(_list_to_multipolygon)

    # Clean up region and label fields
    regions: list[str] = []
    labels: list[str] = []
    for region, label in zip(df_atlas['region'], df_atlas['label']):
        regions.append(region if region is not None else '???')
        labels.append(label if label is not None else '???')
    df_atlas['region'] = regions
    df_atlas['label'] = labels

    # Add 'roi' column for aseg atlas
    if atlas_name == 'aseg':
        df_atlas['roi'] = df_atlas['label']  # df_atlas['hemi'] + '_' + df_atlas['label']  # type: ignore
    elif atlas_name == 'glasser':
        df_atlas['roi'] = [label.split('_')[1] + '_' + label.split('_')[-1] + '_ROI' for label in df_atlas['label']]

    if return_atlas_fname:
        return gpd.GeoDataFrame(df_atlas, geometry='geometry'), atlas_name
    else:
        return gpd.GeoDataFrame(df_atlas, geometry='geometry')


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
        aseg_dict: dict = {
            'x3rd-ventricle': '3rd-Ventricle',
            'x4th-ventricle': '4th-Ventricle',
            'Left-Thalamus-Proper': 'Left-Thalamus',
            'Right-Thalamus-Proper': 'Right-Thalamus',
        }

        geo_df['roi'] = geo_df['roi'].replace(aseg_dict)  # type: ignore

        geo_mg = geo_df.merge(data, on='roi')
        geo_mg = pd.concat([geo_mg, geo_df.query('roi == "???"')])  # add empty cortex back-in

    else:
        geo_mg = geo_df.merge(data, on='roi')
    # Merge and return
    return geo_mg


def atlas2df(atlas: Path, df: pd.DataFrame, col2merge: str) -> gpd.GeoDataFrame:
    """
    Load atlas data from an R .rda file, convert to GeoDataFrame and merge with existing data.

    Parameters
    ----------
    atlas : str
        Name of an atlas or filepath to an .rda atlas file.
        When using a "custom" rda file be aware that the object inside the .rda to extract data (e.g., 'aseg').
        should be labeled according to the atlas itself.
    df : pd.DataFrame
        Pandas Datframe containing the data you want to plot on an atlas.
        Be aware that the information the labels of the atlas should match the labels that you want to plot.
    col2merge : str
        a string denoting the column in your pandas dataframe upon which
        you want to merge the data of your dataframe with the atlas.

    Returns
    -------
    GeoDataFrame
        A GeoDataFrame with 'geometry' a 'roi' column denoting the name of the brain "location"
        on which you merged your data, as well as all the other data in you original pandas dataframe.
    """

    geo_df, atlas_name = rda2gpd(atlas=atlas, return_atlas_fname=True)

    df.rename(columns={col2merge: 'roi'}, inplace=True)

    df_mg = merge_data(df, geo_df, atlas_name)

    return df_mg
