#%%
from ggseg_py.ggseg_py import rda2gpd, merge_data
from ggseg_py.plotting_utils import plot_surface, plot_view, plot_aseg
from ggseg_py.conversion_dicts import aseg_dict
from pathlib import Path
import numpy as np
import pandas as pd

def test_glasser():
    HERE = Path(__file__).parent.parent  
    atlas_path = HERE / "ggseg_py" / "atlases" / "glasser.rda"
    gdf = rda2gpd(atlas_path, 'glasser')
    plot_surface(gdf)

def test_aseg():
    HERE = Path(__file__).parent.parent  
    atlas_path = HERE / "ggseg_py" / "atlases" / "aseg.rda"
    gdf = rda2gpd(atlas_path, 'aseg')
    plot_aseg(gdf)

def test_data_merge():
    HERE = Path(__file__).parent.parent  
    atlas_path = HERE / "ggseg_py" / "atlases" / "aseg.rda"
    test_df = (pd.DataFrame(dict(zip(aseg_dict.values(), 
                                     np.arange(len(aseg_dict.values())))), index=[0])
                 .melt(var_name='StructName', value_name='value'))
    gdf = rda2gpd(atlas_path, 'aseg')
    gdf = merge_data(test_df, geo_df=gdf, atlas_name='aseg')
    
    plot_aseg(gdf, 'value')

def test_dk():
    HERE = Path(__file__).parent.parent  
    atlas_path = HERE / "ggseg_py" / "atlases" / "dk.rda"
    gdf = rda2gpd(atlas_path, 'dk')
    plot_surface(gdf)

def test_val_plotting():
    HERE = Path(__file__).parent.parent  
    atlas_path = HERE / "ggseg_py" / "atlases" / "dk.rda"
    gdf = rda2gpd(atlas_path, 'dk')
    gdf['data2plot'] = np.arange(len(gdf))
    plot_surface(gdf, column='data2plot', cmap='Reds', show_cbar=True)

def test_view_dk():
    HERE = Path(__file__).parent.parent  
    atlas_path = HERE / "ggseg_py" / "atlases" / "dk.rda"
    gdf = rda2gpd(atlas_path, 'dk')
    plot_view(gdf, side='medial', hemi='right')

