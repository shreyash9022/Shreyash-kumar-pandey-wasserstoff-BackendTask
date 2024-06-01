# Import necessary libraries
import queue
import threading
import random
import time
from flask import Flask, request, jsonify
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='load_balancer.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


# Mock API endpoints with varied response times
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


# Load Balancer Class
class LoadBalancer:
    def __init__(self):
        self.request_queues = {
            'FIFO': queue.Queue(),
            'Priority': queue.PriorityQueue(),
            'RoundRobin': queue.Queue()
        }
        self.active_endpoints = {}

    # Function to process requests from different queues
    def process_requests(self, queue_type):
        while True:
            if not self.request_queues[queue_type].empty():
                # Get request from the queue
                api_type, payload = self.request_queues[queue_type].get()

                # Select endpoint based on API type
                if api_type in endpoints:
                    selected_endpoint = random.choice(endpoints[api_type])
                else:
                    selected_endpoint = random.choice([fast_response, slow_response])

                # Simulate request to endpoint
                start_time = time.time()
                response = selected_endpoint()
                response_time = time.time() - start_time

                # Logging response time
                logging.info(f'[{queue_type}] Endpoint response time: {response_time} seconds')
            time.sleep(0.1)


# Initialize Load Balancer instance
lb = LoadBalancer()


# Thread function to process requests from different queues
def process_requests(queue_type):
    lb.process_requests(queue_type)


# Flask route to handle incoming requests
@app.route('/api/<api_type>', methods=['POST'])
def handle_request(api_type):
    payload = request.get_data(as_text=True)
    # Add request to FIFO queue
    lb.request_queues['FIFO'].put((api_type, payload))
    # Add request to Priority queue with random priority
    lb.request_queues['Priority'].put((random.randint(1, 10), api_type, payload))
    # Add request to RoundRobin queue
    lb.request_queues['RoundRobin'].put((api_type, payload))
    return jsonify({"message": "Request received and queued."}), 200


if __name__ == '__main__':
    # Start threads to process requests from different queues
    for queue_type in lb.request_queues:
        threading.Thread(target=process_requests, args=(queue_type,)).start()
    # Run Flask app
    app.run(debug=True)
