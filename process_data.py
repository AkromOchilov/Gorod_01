import pandas as pd

def process_data():
    df = pd.read_csv('df.csv')

    # Convert 'date_accident' to datetime and coerce errors
    df['date_accident'] = pd.to_datetime(df['date_accident'], errors='coerce')

    # Drop rows where 'date_accident' is NaT (not a time)
    df.dropna(subset=['date_accident'], inplace=True)

    # Format 'date_accident' as year-month-day
    df['date_accident'] = df['date_accident'].dt.strftime('%Y-%m-%d')

    # Drop other rows with any null values
    df.dropna(inplace=True)

    df.to_csv('processed_df.csv', index=False)

if __name__ == '__main__':
    process_data()
