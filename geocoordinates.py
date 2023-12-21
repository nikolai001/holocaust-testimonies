import pandas as pdfrom geopy.geocoders import Nominatimfrom tqdm import tqdm# Load data from the CSV file with camp namesfirst_csv = 'testimonies_clean.csv'df = pd.read_csv(first_csv)def Get_Geo_Coordinates(df, column_name):    # Create a geocoding object    geolocator = Nominatim(user_agent="my_geocoder")    # Cache dictionary to store geocoding results    geocode_cache = {}    # Use tqdm to create a progress bar for the loop    for index, element_names in tqdm(enumerate(df[column_name]), total=len(df), desc="Geocoding Progress"):        # Check if the element_names is a string        if isinstance(element_names, str):            # Split the camp names using ',' as a delimiter            elements = element_names.split(',')            for i, element in enumerate(elements, start=1):              #strip the spaces from the element                elements = element_names.split(',')                # Check the cache                if element not in geocode_cache:                    # Use geocoder to get coordinates for the element                    geo_location = geolocator.geocode(element.strip(), timeout=5)                    # Add coordinates to the cache if found                    if geo_location:                        geocode_cache[element] = (geo_location.latitude, geo_location.longitude)    return geocode_cache# Get the Geo_code_caches (dictionaries) from each column:PoB_Cache = Get_Geo_Coordinates(df, 'place_of_birth')Ghetto_cache = Get_Geo_Coordinates(df, 'ghetto')Camps_Cache = Get_Geo_Coordinates(df, 'camps')# Merge individual caches into a single Uber_cache:GeoCode_Uber_cache = {}for cache in [PoB_Cache, Ghetto_cache, Camps_Cache]:    GeoCode_Uber_cache.update(cache)# Create a DataFrame from the cache/dictionarydf_geocode = pd.DataFrame(GeoCode_Uber_cache.values(), index=GeoCode_Uber_cache.keys(), columns=['Latitude', 'Longitude'])df_geocode.reset_index(inplace=True)df_geocode.rename(columns={'index': 'Place'}, inplace=True)# Save DataFrame with coordinates to a new CSV fileoutput_csv_path = 'Uber_cache_geocodes.csv'df_geocode.to_csv(output_csv_path, index=False)