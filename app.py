from flask import Flask, render_template, request, redirect, url_for
from auth import store_credentials, verify_credentials
import pandas as pd
import plotly
import plotly.express as px
import json
import folium
import geopandas as gpd
from folium.plugins import MarkerCluster


app = Flask(__name__)

df = pd.read_csv('processed_df.csv')

# Extract unique values for filters
years = sorted(pd.to_datetime(df['date_accident']).dt.year.unique())
accident_types = sorted(df['accident_type'].dropna().unique())
districts = sorted(df['district'].dropna().unique())
road_conditions = sorted(df['road_condition'].dropna().unique())
weather_conditions = sorted(df['weather_condition'].dropna().unique())
road_parts = sorted(df['road_part'].dropna().unique())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    # Retrieve filter parameters from request
    selected_year = request.args.get('year')
    selected_accident_type = request.args.get('accident_type')
    selected_district = request.args.get('district')
    selected_road_condition = request.args.get('road_condition')
    selected_weather_condition = request.args.get('weather_condition')
    selected_road_part = request.args.get('road_part')

    # Filter the DataFrame based on the parameters
    filtered_df = df.copy()
    if selected_year:
        filtered_df = filtered_df[pd.to_datetime(filtered_df['date_accident']).dt.year == int(selected_year)]
    if selected_accident_type:
        filtered_df = filtered_df[filtered_df['accident_type'] == selected_accident_type]
    if selected_district:
        filtered_df = filtered_df[filtered_df['district'] == selected_district]
    if selected_road_condition:
        filtered_df = filtered_df[filtered_df['road_condition'] == selected_road_condition]
    if selected_weather_condition:
        filtered_df = filtered_df[filtered_df['weather_condition'] == selected_weather_condition]
    if selected_road_part:
        filtered_df = filtered_df[filtered_df['road_part'] == selected_road_part]

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    total_pages = (len(filtered_df) + per_page - 1) // per_page  # Calculate total pages
    df_paginated = filtered_df.iloc[(page - 1) * per_page:page * per_page]

    # Convert filtered and paginated dataframe to HTML table
    df_html = df_paginated.to_html(classes='table table-striped', border=0, index=False)

    # Creating a Plotly figure
    gdf = gpd.GeoDataFrame(df_paginated, geometry=gpd.points_from_xy(
        df_paginated['longitude'], df_paginated['latitude']))

    # Create a heatmap using Folium's MarkerCluster plugin
    map = folium.Map(location=[41.3775, 64.5853], zoom_start=8, width=600,
                     height=300)  # Adjust width and height as needed
    marker_cluster = MarkerCluster().add_to(
        map)  # Use the plugin to create the cluster

    for i in range(len(gdf)):
        folium.Marker([gdf.iloc[i]['latitude'], gdf.iloc[i]['longitude']],
                      icon=folium.Icon(color='red', prefix='fa',
                                       icon='circle'),
                      popup=f"Accident ID: {gdf.iloc[i]['id']}").add_to(
            marker_cluster)

    # Generate map HTML
    map_html = map._repr_html_()

    return render_template('data.html', table=df_html, years=years, accident_types=accident_types,
                           districts=districts, road_conditions=road_conditions,
                           weather_conditions=weather_conditions, road_parts=road_parts,
                           total_pages=total_pages, current_page=page, map_html=map_html)

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        store_credentials(email, password)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if verify_credentials(email, password):
            return redirect(url_for('index'))
        else:
            return 'Login Failed'
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
