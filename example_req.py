import pandas as pd
import requests

def load_and_prepare_data(csv_path: str):
    """
    Load time series data from CSV file.
    Expects CSV to have at least two columns:
    - date column (can be named 'date', 'timestamp', etc.)
    - value column (can be named 'value', 'sales', etc.)
    """
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Identify date column (assumes first column is date)
    date_col = df.columns[0]
    value_col = df.columns[1]
    
    # Convert dates to datetime if they aren't already
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Sort by date
    df = df.sort_values(by=date_col)
    
    # Prepare data in the format expected by the API
    data = {
        "data": {
            "dates": df[date_col].dt.strftime('%Y-%m-%d').tolist(),
            "values": df[value_col].tolist()
        },
        "periods": 30,  # Forecast 30 periods ahead
        "model_parameters": {
            "changepoint_prior_scale": 0.08,
            "seasonality_prior_scale": 12.0,
            "seasonality_mode": "multiplicative",
            "yearly_seasonality": True,
            "growth": "linear"  # Changed to linear as example
        },
        "return_components": True
    }
    
    return data

def get_forecast(data: dict, api_url: str = "http://localhost:8000/forecast/"):
    """Send request to the forecasting service and get predictions"""
    try:
        response = requests.post(api_url, json=data)
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

def save_forecast(forecast: dict, output_path: str):
    """Save the forecast results to a CSV file"""
    # Create DataFrame with forecast results
    df = pd.DataFrame({
        'date': forecast['forecast_dates'],
        'forecast': forecast['forecast_values'],
        'lower_bound': forecast['forecast_lower_bound'],
        'upper_bound': forecast['forecast_upper_bound']
    })
    
    # Add components if they exist
    if 'components' in forecast and forecast['components']:
        for component, values in forecast['components'].items():
            df[f'component_{component}'] = values
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Forecast saved to {output_path}")

def main():
    csv_path = "Electric_Production.csv"  
    output_path = "results.csv"
    
    # Load and prepare data
    data = load_and_prepare_data(csv_path)
    
    # Get forecast
    forecast = get_forecast(data)
    
    if forecast:
        # Save results
        save_forecast(forecast, output_path)
        
        # Print some basic stats
        print("\nForecast Summary:")
        print(f"Number of periods forecasted: {len(forecast['forecast_dates'])}")
        print(f"Last historical date: {forecast['forecast_dates'][0]}")
        print(f"Last forecast date: {forecast['forecast_dates'][-1]}")

if __name__ == "__main__":
    main()