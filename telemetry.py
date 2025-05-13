from prometheus_client import Counter, start_http_server

# Start Prometheus metrics server on port 8000
start_http_server(8000)

# Define a request counter
request_counter = Counter(
    'flask_bookstore_requests_total',
    'Total HTTP requests received'
)

__all__ = ["request_counter"]
