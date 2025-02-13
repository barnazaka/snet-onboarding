# Time Series Prediction Service

A RESTful API service for time series forecasting built with FastAPI and Prophet. This service provides scalable, customizable time series predictions through a simple HTTP interface.

## Features

- **RESTful API**: Easy-to-use HTTP endpoints for time series forecasting
- **Customizable Forecasting**: Extensive model parameter customization options
- **Rich Output**: Returns predictions with confidence intervals and seasonal components

## Components

### Backend Service (`app.py`)
- FastAPI application providing the REST API
- Prophet model integration for forecasting
- Customizable model parameters

### Example Request (`example_req.py`)
- CSV data loading and preprocessing
- API interaction utilities
- Results saving and formatting
- Basic forecast summary statistics

## Installation

1. Clone the repository
2. Create a virtual environment (for example with venv):
```
python -m venv venv
```
3. Install requirements:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server
```bash
python app.py
```
The server will start at `http://localhost:8000`

### Making Predictions
1. Prepare your time series data in CSV format with date and value columns
2. Use the client script:
```bash
python example_req.py
```

### API Endpoints

- `POST /forecast/`: Create time series forecasts
- `GET /parameters/default`: Get default model parameters

## Example Request

```python
{
    "data": {
        "dates": ["2023-01-01", ...],
        "values": [100, ...]
    },
    "periods": 30,
    "model_parameters": {
        "changepoint_prior_scale": 0.08,
        "seasonality_mode": "multiplicative",
        "yearly_seasonality": true
    },
    "return_components": true
}
```

## Response Format

```python
{
    "forecast_dates": ["2023-02-01", ...],
    "forecast_values": [120.5, ...],
    "forecast_lower_bound": [115.2, ...],
    "forecast_upper_bound": [125.8, ...],
    "components": {
        "trend": [110.2, ...],
        "yearly": [10.3, ...],
        "weekly": [0.5, ...]
    }
}
```

## Dependencies

- Requests
- FastAPI
- Numpy
- Prophet
- Pandas
- Pydantic
- Uvicorn