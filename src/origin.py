from geopandas.tools import geocode
import geopandas as gpd

def geocode_address(address: str) -> gpd.GeoDataFrame:
    """Geocode address using Nominatim
    address [str]: address to be geocoded
    """
    # geocode address
    gdf = geocode(address, provider='nominatim', user_agent='autogis_xx', timeout=4)
    return gdf

def geocode_point(lng: float, lat: float) -> gpd.GeoDataFrame:
    """Point into GeoDataFrame
    lng [float]: longitude of the point
    lat [float]: latitude of the point
    """
    # geocode point
    gdf = gpd.GeoDataFrame(geometry=[Point((lng,lat))], crs='EPSG:4326')
    return gdf

def create_bbox(gdf: gpd.GeoDataFrame, buffer: float = 60000, crs: int=25832) -> gpd.GeoDataFrame:
    """Create bounding box around a point
    gdf [gpd.GeoDataFrame]: GeoDataFrame containing a point
    buffer [float]: buffer around the point in meters
    """
    # create bounding box
    gdf_crs = gdf.to_crs(f"EPSG:{crs}")
    bbox = gdf_crs.buffer(buffer)
    bbox = bbox.to_crs("EPSG:4326")
    bbox = bbox.envelope.to_frame(name='geometry')
    return bbox