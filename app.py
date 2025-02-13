from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prophet import Prophet
import pandas as pd
from typing import List, Dict, Optional

app = FastAPI(title="Onboarders Example Time Series Prediction Service")

class TimeSeriesData(BaseModel):
    dates: List[str]
    values: List[float]

class ProphetParameters(BaseModel):
    # Core Parameters
    changepoint_prior_scale: float = Field(
        default=0.05,
        gt=0,
        description="Flexibility of the trend changes. Higher values allow more flexibility."
    )
    seasonality_prior_scale: float = Field(
        default=10.0,
        gt=0,
        description="Strength of the seasonality model. Higher values allow stronger seasonal patterns."
    )
    holidays_prior_scale: float = Field(
        default=10.0,
        gt=0,
        description="Strength of the holiday effects. Higher values allow stronger holiday effects."
    )
    seasonality_mode: str = Field(
        default="additive",
        pattern="^(additive|multiplicative)$",
        description="Type of seasonality, either 'additive' or 'multiplicative'"
    )
    
    # Seasonality Parameters
    yearly_seasonality: Optional[bool] = Field(
        default=True,
        description="Whether to include yearly seasonality"
    )
    weekly_seasonality: Optional[bool] = Field(
        default=True,
        description="Whether to include weekly seasonality"
    )
    daily_seasonality: Optional[bool] = Field(
        default=False,
        description="Whether to include daily seasonality"
    )
    
    # Growth Parameters
    growth: str = Field(
        default="linear",
        pattern="^(linear|logistic|flat)$",
        description="Type of growth trend: 'linear', 'logistic', or 'flat'"
    )
    cap: Optional[float] = Field(
        default=None,
        description="Growth cap for logistic growth"
    )
    floor: Optional[float] = Field(
        default=None,
        description="Growth floor for logistic growth"
    )
    
    # Changepoint Parameters
    n_changepoints: int = Field(
        default=25,
        ge=0,
        description="Number of potential changepoints"
    )
    changepoint_range: float = Field(
        default=0.8,
        gt=0,
        le=1,
        description="Proportion of history where changepoints are considered"
    )

class ForecastRequest(BaseModel):
    data: TimeSeriesData
    periods: int = Field(
        default=30,
        gt=0,
        description="Number of periods to forecast"
    )
    model_parameters: Optional[ProphetParameters] = Field(
        default=None,
        description="Custom Prophet model parameters"
    )
    return_components: bool = Field(
        default=False,
        description="Whether to return trend and seasonal components"
    )

class ForecastResponse(BaseModel):
    forecast_dates: List[str]
    forecast_values: List[float]
    forecast_lower_bound: List[float]
    forecast_upper_bound: List[float]
    components: Optional[Dict[str, List[float]]] = None

def prepare_data(data: TimeSeriesData) -> pd.DataFrame:
    """Convert input data to Prophet's required format."""
    return pd.DataFrame({
        'ds': pd.to_datetime(data.dates),
        'y': data.values
    })

def configure_prophet_model(params: ProphetParameters) -> Prophet:
    """Configure Prophet model with custom parameters."""
    model_args = {
        'changepoint_prior_scale': params.changepoint_prior_scale,
        'seasonality_prior_scale': params.seasonality_prior_scale,
        'holidays_prior_scale': params.holidays_prior_scale,
        'seasonality_mode': params.seasonality_mode,
        'yearly_seasonality': params.yearly_seasonality,
        'weekly_seasonality': params.weekly_seasonality,
        'daily_seasonality': params.daily_seasonality,
        'growth': params.growth,
        'n_changepoints': params.n_changepoints,
        'changepoint_range': params.changepoint_range
    }
    
    # Add capacity parameters for logistic growth
    if params.growth == 'logistic':
        if params.cap is None or params.floor is None:
            raise ValueError("Cap and floor must be specified for logistic growth")
        model_args['growth'] = 'logistic'
        model_args['cap'] = params.cap
        model_args['floor'] = params.floor
    
    return Prophet(**model_args)

@app.post("/forecast/", response_model=ForecastResponse)
async def create_forecast(request: ForecastRequest):
    try:
        # Prepare the input data
        df = prepare_data(request.data)
        
        # Configure and train the model
        model_params = request.model_parameters or ProphetParameters()
        model = configure_prophet_model(model_params)
        model.fit(df)
        
        # Create future dates for forecasting
        future = model.make_future_dataframe(periods=request.periods)
        
        # If using logistic growth, set cap and floor for future dates
        if model_params.growth == 'logistic':
            future['cap'] = model_params.cap
            future['floor'] = model_params.floor
        
        # Make predictions
        forecast = model.predict(future)
        
        # Prepare the response
        response_data = {
            'forecast_dates': forecast.ds[-request.periods:].dt.strftime('%Y-%m-%d').tolist(),
            'forecast_values': forecast.yhat[-request.periods:].tolist(),
            'forecast_lower_bound': forecast.yhat_lower[-request.periods:].tolist(),
            'forecast_upper_bound': forecast.yhat_upper[-request.periods:].tolist()
        }
        
        # Add components if requested
        if request.return_components:
            components = {
                'trend': forecast.trend[-request.periods:].tolist(),
                'yearly': forecast.yearly[-request.periods:].tolist() if 'yearly' in forecast else None,
                'weekly': forecast.weekly[-request.periods:].tolist() if 'weekly' in forecast else None,
                'daily': forecast.daily[-request.periods:].tolist() if 'daily' in forecast else None
            }
            response_data['components'] = {k: v for k, v in components.items() if v is not None}
        
        return ForecastResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/parameters/default")
async def get_default_parameters():
    """Return the default model parameters and their descriptions."""
    return ProphetParameters.model_json_schema()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

