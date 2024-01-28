from flask import Flask, render_template, request, redirect, url_for
from auth import store_credentials, verify_credentials
import pandas as pd
import plotly
import plotly.express as px
import json
import folium
import geopandas as gpd
from folium.plugins import MarkerCluster
import os

app = Flask(__name__)

# Load your dataset
df = pd.read_csv('processed_df.csv')

# Extract unique values for dropdown menus
years = sorted(pd.to_datetime(df['date_accident']).dt.year.unique())
accident_types = sorted(df['accident_type'].dropna().unique())
districts = sorted(df['district'].dropna().unique())
vehicle_models_uz = sorted(df['vehicle_model_uz'].dropna().unique())


def calculate_risk_level(df, district, vehicle_model):
    district_df = df[df['district'] == district]
    vehicle_count = len(
        district_df[district_df['vehicle_model_uz'] == vehicle_model])
    total_count = len(district_df)
    return (vehicle_count / total_count) * 100 if total_count > 0 else 0


@app.route('/data', methods=['GET'])
def data():
    selected_year = request.args.get('year')
    selected_accident_type = request.args.get('accident_type')
    selected_district = request.args.get('district')
    selected_vehicle_model = request.args.get('vehicle_model_uz')
    page = request.args.get('page', 1, type=int)

    filtered_df = df.copy()
    if selected_year:
        filtered_df = filtered_df[
            pd.to_datetime(filtered_df['date_accident']).dt.year == int(
                selected_year)]
    if selected_accident_type:
        filtered_df = filtered_df[
            filtered_df['accident_type'] == selected_accident_type]
    if selected_district:
        filtered_df = filtered_df[filtered_df['district'] == selected_district]

    total_rows = len(filtered_df)
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page
    paginated_df = filtered_df.iloc[start:end]

    risk_level = None
    if selected_district and selected_vehicle_model:
        risk_level = calculate_risk_level(df, selected_district,
                                          selected_vehicle_model)

    return render_template('data.html',
                           table=paginated_df.to_html(classes='dataframe'),
                           years=years, accident_types=accident_types,
                           districts=districts,
                           vehicle_models_uz=vehicle_models_uz,
                           risk_level=risk_level,
                           total_pages=(total_rows // per_page),
                           current_page=page)
@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/reports')
def reports():
    directory = os.path.join(app.static_folder, "pdfs")
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    return render_template('reports.html', pdf_files=pdf_files)

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
