import geopandas as gpd
import pandas as pd
import numpy as np
import os.path
import folium

def process_data():
    df_final_name = "df_final.csv"
    df_final = None

    if not os.path.isfile(df_final_name):

        df_manzanas = gpd.read_file('predata/MGN2021_URB_MANZANA')
        df_manzanas = df_manzanas[df_manzanas['COD_MPIO'] == '05001']

        df_copy = df_manzanas.copy()

        df_copy = df_copy.to_crs(epsg=32618)

        df_copy['area'] = df_copy.geometry.area
        df_manzanas['area'] = df_copy['area']

        df_barrios = gpd.read_file('predata/barrios.geojson')
        df_barrios = df_barrios.to_crs(epsg=4326)
        df_manzanas = df_manzanas.to_crs(epsg=4326)

        joined = gpd.sjoin(df_manzanas, df_barrios, how="inner", op="intersects")

        # Seleccionar las columnas que quieres conservar en el nuevo DataFrame
        cols = ['COD_DPTO', 'COD_MPIO', 'COD_CLASE', 'COD_CPOB', 'COD_SECC',
                            'COD_DANE', 'COD_AG', 'TIPO_CTSTR', 'COD_CTSTR', 'ANO_VGNC',
                            'ANO_ACTLZ', 'REVI_CAMPO', 'LATI', 'LONG', 'VIV', 'SHAPE_Leng',
                            'SHAPE_Area', 'FT_ACT_VIV', 'geometry', 'area', 'NOMBRE']

        # Crear el nuevo DataFrame con las columnas deseadas
        df_final = joined[cols]

        df_poblacion_barrios = pd.read_csv('predata/poblacion-barrios.csv')

        df_area_barrio = df_final.groupby('NOMBRE')['area'].sum().reset_index()
        df_area_barrio.columns = ['NOMBRE', 'AREA_TOTAL_BARRIO']

        df_final = pd.merge(df_final, df_area_barrio, on='NOMBRE', how='left')
        df_final = pd.merge(df_final, df_poblacion_barrios, on='NOMBRE', how='left')
        df_final['POBLACION_MANZANA'] = df_final['POBLACION'] * df_final['area']/df_final['AREA_TOTAL_BARRIO']

        df_final['POBLACION_MANZANA'].fillna(0, inplace=True)
        df_final['POBLACION_MANZANA'] = np.ceil(df_final['POBLACION_MANZANA'])

        
        df_final.to_csv(df_final_name, index=False)
        
        mapa = folium.Map(location=[df_final.geometry.centroid.y.mean(), df_final.geometry.centroid.x.mean()], zoom_start=13)

        for idx, row in df_final.iterrows():
            area_formateada = "{:.2f}".format(row['area'])
            etiqueta = f"Barrio: {row['NOMBRE']}, Área: {area_formateada} m², Población: {row['POBLACION_MANZANA']}"
            folium.GeoJson(row.geometry, tooltip=etiqueta).add_to(mapa)

        mapa.save('mapa.html')
    else:
        df_final = pd.read_csv(df_final_name)
    return df_final
