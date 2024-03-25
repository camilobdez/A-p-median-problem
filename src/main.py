import folium
import numpy as np
from process_data import process_data

data = process_data()

mapa = folium.Map(location=[data.geometry.centroid.y.mean(), data.geometry.centroid.x.mean()], zoom_start=13)

for idx, row in data.iterrows():
    area_formateada = "{:.2f}".format(row['area'])
    etiqueta = f"Barrio: {row['NOMBRE']}, Área: {area_formateada} m², Población: {row['POBLACION_MANZANA']}"
    folium.GeoJson(row.geometry, tooltip=etiqueta).add_to(mapa)

lat_min, lat_max = 6.1925, 6.35
lon_min, lon_max = -75.6461, -75.5314

np.random.seed(0)
latitudes = np.random.uniform(lat_min, lat_max, 5000)
longitudes = np.random.uniform(lon_min, lon_max, 5000)

for lat, lon in zip(latitudes, longitudes):
    folium.CircleMarker(location=[lat, lon], radius=2, color='red', fill=True, fill_color='blue').add_to(mapa)


mapa.save('mapa_puntos.html')
