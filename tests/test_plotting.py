#%%
from ggseg_py.ggseg_py import rda2gpd, merge_data
from ggseg_py.plotting_utils import plot_surface, plot_view, plot_aseg
from pathlib import Path
import numpy as np
import pandas as pd

def test_glasser():
    HERE = Path(__file__).parent.parent  
    atlas_path = HERE / "ggseg_py" / "atlases" / "glasser.rda"
    gdf = rda2gpd(atlas_path)
    plot_surface(gdf)

def test_aseg():

    gdf = rda2gpd('aseg')
    plot_aseg(gdf)

def test_data_merge():

    gdf = rda2gpd('aseg')
    

    test_df = (pd.DataFrame(dict(zip(gdf['roi'].values, 
                                     np.arange(len(gdf['roi'].values)))), index=[0])
                 .melt(var_name='roi', value_name='value'))
    gdf = merge_data(test_df, geo_df=gdf, atlas_name='aseg')
    
    plot_aseg(gdf, 'value')

def test_dk():

    gdf = rda2gpd('dk')
    plot_surface(gdf)

def test_val_plotting():
    HERE = Path(__file__).parent.parent  
    atlas_path = HERE / "ggseg_py" / "atlases" / "dk.rda"
    gdf = rda2gpd(atlas_path)
    gdf['data2plot'] = np.arange(len(gdf))
    plot_surface(gdf, value='data2plot', cmap='Reds', show_cbar=True)

def test_view_dk():

    gdf = rda2gpd('dk')
    plot_view(gdf, side='medial', hemi='right')

