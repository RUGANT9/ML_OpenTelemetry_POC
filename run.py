from app import create_app
from telemetry import request_counter

# Create the Flask app
app = create_app()

@app.after_request
def count_requests(response):
    request_counter.inc()
    return response

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
