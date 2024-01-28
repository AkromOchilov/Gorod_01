import pandas as pd
import plotly.express as px

df = pd.read_csv('processed_df.csv')

# Assuming df is your DataFrame with data for the heatmap
fig_heatmap = px.density_heatmap(df, x="longitude", y="latitude", title="Traffic Accident Heatmap")
graphJSON_heatmap = fig_heatmap.to_json()
