import grpc
import service_pb2
import service_pb2_grpc

def run():
    # Create a channel
    channel = grpc.insecure_channel("localhost:50051")
    stub = service_pb2_grpc.GetForecastServiceStub(channel)
    
    try:
        # Create the request
        data_map = service_pb2.DataMap(
            dates=["2024-01-01", "2024-01-02"],
            values=[100.0, 200.0]
        )
        
        model_params = service_pb2.ModelParameters(
            changepoint_prior_scale=0.08,
            seasonality_prior_scale=12.0,
            seasonality_mode="additive",
            yearly_seasonality=True,
            growth="linear"
        )
        
        data = service_pb2.Data(
            data=data_map,
            periods=30,
            model_parameters=model_params,
            return_components=True
        )
        
        request = service_pb2.ForecastRequest(
            data=data,
            api_url="http://example.com"
        )
        
        print("Sending request:", request)  # Debug print
        
        # Make the call
        response = stub.GetForecast(request)
        
        # Print the response
        print("\nForecast Response:")
        print(f"Dates: {response.forecast_dates}")
        print(f"Values: {response.forecast_values}")
        print(f"Lower Bounds: {response.forecast_lower_bound}")
        print(f"Upper Bounds: {response.forecast_upper_bound}")
        print("Components:")
        for name, component in response.components.items():
            print(f"  {name}: {component.values}")
            
    except grpc.RpcError as e:
        print(f"RPC Error: {e.code()}")
        print(f"Details: {e.details()}")

if __name__ == "__main__":
    run()