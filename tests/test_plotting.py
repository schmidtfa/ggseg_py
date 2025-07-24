#%%
from ggseg_py.ggseg_py import rda2gpd
from ggseg_py.plotting_utils import plot_surface, plot_view, plot_aseg
from pathlib import Path

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

def test_dk():
    HERE = Path(__file__).parent.parent  
    atlas_path = HERE / "ggseg_py" / "atlases" / "dk.rda"
    gdf = rda2gpd(atlas_path, 'dk')
    plot_surface(gdf)

def test_view_dk():
    HERE = Path(__file__).parent.parent  
    atlas_path = HERE / "ggseg_py" / "atlases" / "dk.rda"
    gdf = rda2gpd(atlas_path, 'dk')
    plot_view(gdf, side='medial', hemi='right')

