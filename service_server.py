import grpc
from concurrent import futures
import service_pb2
import service_pb2_grpc

class GetForecastService(service_pb2_grpc.GetForecastServiceServicer):
    def GetForecast(self, request, context):
        print("GetForecast called with request:", request)  # Debug print
        
        try:
            # Validate the request
            if not request.data.data.dates:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Dates should not be empty")
            if not request.data.data.values:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Values should not be empty")
            if not request.data.periods:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Periods should not be empty")
            
            # Create sample forecast response
            forecast_dates = ["2024-01-01", "2024-01-02"]
            forecast_values = [0.2, 0.5]
            forecast_lower_bound = [0.3, 0.4]
            forecast_upper_bound = [0.4, 0.5]
            
            # Create components
            trend_component = service_pb2.ForecastComponent(values=[0.3, 0.9])
            seasonal_component = service_pb2.ForecastComponent(values=[0.1, 0.2])
            
            components = {
                "trend": trend_component,
                "seasonal": seasonal_component
            }
            
            # Return the forecast
            return service_pb2.Forecast(
                forecast_dates=forecast_dates,
                forecast_values=forecast_values,
                forecast_lower_bound=forecast_lower_bound,
                forecast_upper_bound=forecast_upper_bound,
                components=components
            )
            
        except Exception as e:
            print(f"Error in GetForecast: {str(e)}")  # Debug print
            context.abort(grpc.StatusCode.INTERNAL, f"Internal server error: {str(e)}")

class SaveForecastService(service_pb2_grpc.SaveForecastServiceServicer):
    def SaveForecast(self, request, context):
        print("SaveForecast called")
        try:
            if not request.forecast.forecast_dates:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Forecast dates should not be empty")
            
            success = True
            message = "Success"
            return service_pb2.SaveForecastResponse(success=success, message=message)
            
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Internal server error: {str(e)}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_GetForecastServiceServicer_to_server(GetForecastService(), server)
    service_pb2_grpc.add_SaveForecastServiceServicer_to_server(SaveForecastService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("🚀 gRPC Server running on port 50051...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()