import random
import time
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='load_balancer.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


# Mock API endpoints
def fast_response():
    time.sleep(0.1)
    return jsonify({"message": "Fast response"}), 200


def slow_response():
    time.sleep(2)
    return jsonify({"message": "Slow response"}), 200


# Dictionary of API endpoints
endpoints = {
    'REST': [fast_response, slow_response],
    'GraphQL': [fast_response],
    'gRPC': [slow_response]
}


# Load Balancer Function
def load_balancer(api_type, payload):
    # Logging request
    logging.info(f'Received request for API type: {api_type} with payload size: {len(payload)}')

    # Routing logic
    if api_type in endpoints:
        # Example Custom Criteria: Different routing based on payload size
        if len(payload) > 1000:
            selected_endpoint = slow_response
        else:
            # Randomized routing
            selected_endpoint = random.choice(endpoints[api_type])
    else:
        selected_endpoint = random.choice([fast_response, slow_response])

    # Logging endpoint selection
    logging.info(f'Routing to endpoint: {selected_endpoint.__name__}')

    # Simulate request to endpoint
    start_time = time.time()
    response = selected_endpoint()
    response_time = time.time() - start_time

    # Logging response time
    logging.info(f'Endpoint response time: {response_time} seconds')

    return response


# Flask route to handle incoming requests
@app.route('/api/<api_type>', methods=['POST'])
def handle_request(api_type):
    payload = request.get_data(as_text=True)
    return load_balancer(api_type, payload)


if __name__ == '__main__':
    app.run(debug=True)
