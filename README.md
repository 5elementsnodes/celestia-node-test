# Celestia Node Test Tools - Load 

This script allows you to test the performance of your Celestia API endpoint by making multiple requests to it and measuring the response time, latency, and number of errors and timeouts. It uses the `requests` library to make HTTP requests, and `concurrent.futures` to run multiple requests in parallel using multiple threads.

## Prerequisites

This script requires Python 3.x and the `requests` library. You can install the `requests` library using pip:

```
pip install requests
```

## Usage

To use the script, simply run it from the command line and provide the endpoint URL and the authorization token using the `-a` or `--auth` flag. You can also specify the number of requests to make using the `-c` or `--calls` flag, the number of threads to use using the `-t` or `--threads` flag, and the number of times to retry failed requests using the `-r` or `--retry` flag.

--> Note: This tool is structured to make an RPC call. Celestia nodes uses port 26658 by default. <--

```
python api_request_tester.py <endpoint> -a <auth_token> [-c <num_calls>] [-t <num_threads>] [-r <retry_count>]
```

## Example

Here's an example command that tests an API endpoint with 500 requests using 20 threads and a retry count of 3, and provides the authorization token:

```
python api_request_tester.py https://example.com/api -a abcdef123456 -c 500 -t 20 -r 3
```
```
python api_request_tester.py http://IP:26658 -a abcdef123456 -c 500 -t 20 -r 3
```

## Flags

* `endpoint`: The URL of the API endpoint to test.
* `-c`, `--calls`: The number of requests to make to the API endpoint (default 100).
* `-t`, `--threads`: The number of threads to use for making requests (default 10).
* `-r`, `--retry`: The number of times to retry a failed request (default 0).
* `-a`, `--auth`: The authorization token to use for making requests to the API endpoint.

## Output

The script will output the following information after running:

* `Test time`: The total time taken to run the test.
* `Number of calls`: The number of requests made to the API endpoint.
* `Average time per call`: The average time taken to receive a response from the API endpoint.
* `Endpoint API latency`: The average time taken by the API endpoint to process the request.
* `Total errors`: The total number of errors encountered while making requests.
* `Total timeouts`: The total number of requests that timed out waiting for a response.
