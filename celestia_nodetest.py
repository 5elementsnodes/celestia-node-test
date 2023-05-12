import threading
import time
import requests
import sys
import argparse
import concurrent.futures

parser = argparse.ArgumentParser()
parser.add_argument("endpoint", help="the endpoint to call")
parser.add_argument("-c", "--calls", metavar='', help="number of calls to make (default 1000)", type=int, default=1000)
parser.add_argument("-t", "--threads", metavar='', help="number of threads to use (default 100)", type=int, default=100)
parser.add_argument("-r", "--retry", metavar='', help="number of times to retry a failed call (default 0)", type=int, default=0)
parser.add_argument("-a", "--auth", metavar='', help="authorization token for the API", required=True)
args = parser.parse_args()

num_calls = args.calls
num_threads = args.threads
retry_count = args.retry
authorization = args.auth

if num_calls <= 0:
    raise ValueError("Number of calls must be greater than zero.")
if num_threads <= 0:
    raise ValueError("Number of threads must be greater than zero.")

start = time.monotonic()

total_time = 0
total_latency = 0
total_errors = 0
total_timeouts = 0


def make_request(i, stop_event):
    attempt = 0
    while attempt <= retry_count:
        try:
            if stop_event.is_set():
                break
            start_time = time.monotonic()
            headers = {'Content-Type': 'application/json'}
            if authorization:
                headers['Authorization'] = f'Bearer {authorization}'
            response = requests.post(args.endpoint,
                                     headers=headers,
                                     json={'jsonrpc': '2.0', 'method': 'header.SyncState', 'params': [], 'id': 1},
                                     timeout=15)
            end_time = time.monotonic()
            response.raise_for_status()
            data = response.json()
            time_total = response.elapsed.total_seconds() * 1000
            latency = (end_time - start_time) * 1000 - time_total
            return time_total, latency, None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                stop_event.set()
                return None, None, e
            else:
                print(f"HTTP error: {e}. Endpoint: {args.endpoint}.")
                return None, None, e
        except requests.exceptions.RequestException as e:
            if attempt == retry_count:
                print(f"Request Exception error: {e}. Endpoint: {args.endpoint}.")
                return None, None, e
            else:
                attempt += 1
                time.sleep(1)
                if isinstance(e, requests.exceptions.ReadTimeout):
                    print(f"ReadTimeout error: {e}. Endpoint: {args.endpoint}. Attempt: {attempt}.")
                    continue
                else:
                    print(f"Request Exception error: {e}. Endpoint: {args.endpoint}. Attempt: {attempt}.")
                    continue


with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [executor.submit(make_request, i, threading.Event()) for i in range(num_calls)]

    for i, future in enumerate(concurrent.futures.as_completed(futures)):
        try:
            time_total, latency, error = future.result(timeout=15)
            if time_total:
                total_time += time_total
                total_latency += latency
                if time_total >= 2000:
                    total_timeouts += 1
                    print("Timeout error: waited for 15 seconds.")
            if error:
                print(f"Error: {error}")
                total_errors += 1

            progress = (i + 1) / num_calls * 100
            sys.stdout.write(f"\rProgress: {progress:.1f}%")
            sys.stdout.flush()
        except requests.exceptions.ReadTimeout:
            print("\nTimeout error: read timed out.")
        except concurrent.futures.TimeoutError:
            print("Timeout error: waited for 15 seconds.")
            total_timeouts += 1
        except Exception as e:
            print(f"Error: {e}")
            total_errors += 1

        if error and error.response.status_code == 401:
            print("\nStopping execution due to unauthorized Auth Token")
            for future in futures[i+1:]:
                future.cancel()
            executor.shutdown(wait=False)
            break


end = time.monotonic()

avg_latency = total_latency / num_calls
if avg_latency < 1000:
    latency_unit = "ms"
    latency_display = f"{avg_latency:.2f}"
else:
    latency_unit = "s"
    latency_display = f"{avg_latency/1000:.2f}"

print(f"\nTest time: {round((end - start), 2)} s")
print(f"Number of calls: {num_calls}")
print(f"Number of requests/sec: {num_calls / (end - start):.2f}")
print(f"Average API latency: {latency_display} {latency_unit}")
print(f"Total errors: {total_errors}")
print(f"Total timeouts: {total_timeouts}")
