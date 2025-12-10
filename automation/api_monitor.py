import requests
import time
import json
import csv
import argparse
import schedule

ENDPOINTS = [
    "https://api.example.com/health",
    "https://api.anotherexample.com/status",
    "https://httpbin.org/status/404",
]

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1419602714400129035/7eVTf2l9JybO5_E5aAy0fMNOqgly3bWvGFJMlJcHw29q0P5KaJAAFPuHuAi0dVhanLzq"


def send_discord_alert(endpoint, error):
    message = f"**API Monitoring Alert:** Endpoint `{endpoint}` is down! Error: {error}"
    payload = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Failed to send Discord alert: {e}")


def check_endpoints(output_format, output_file):
    results = []

    for endpoint in ENDPOINTS:
        start_time = time.time()
        try:
            response = requests.get(endpoint, timeout=10)
            response_time = (time.time() - start_time) * 1000
            status_code = response.status_code

            if status_code >= 400:
                send_discord_alert(endpoint, f"Status code {status_code}")

            results.append(
                {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "endpoint": endpoint,
                    "status_code": status_code,
                    "response_time_ms": round(response_time, 2),
                    "status": "UP",
                }
            )

        except requests.exceptions.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            send_discord_alert(endpoint, str(e))
            results.append(
                {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "endpoint": endpoint,
                    "status_code": "N/A",
                    "response_time_ms": round(response_time, 2),
                    "status": "DOWN",
                }
            )

    save_results(results, output_format, output_file)


def save_results(results, output_format, output_file):
    try:
        if output_format == "json":
            with open(output_file, "a") as f:
                for res in results:
                    json.dump(res, f)
                    f.write("\n")

        elif output_format == "csv":
            file_exists = False
            try:
                with open(output_file, "x") as f:
                    pass
            except FileExistsError:
                file_exists = True

            with open(output_file, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerows(results)

        print(f"Results saved to {output_file}")

    except Exception as e:
        print(f"Error saving results: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor API endpoints.")
    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format for results.",
    )
    parser.add_argument(
        "-o", "--output", default="api_monitor_results.json", help="Output file path."
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=0,
        help="Interval in minutes to run the check. 0 means run once.",
    )

    args = parser.parse_args()

    if args.output == "api_monitor_results.json" and args.format == "csv":
        args.output = "api_monitor_results.csv"

    if args.interval > 0:
        print(f"Running check every {args.interval} minutes. Press Ctrl+C to stop.")
        schedule.every(args.interval).minutes.do(
            check_endpoints, output_format=args.format, output_file=args.output
        )
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        print("Running a single check...")
        check_endpoints(output_format=args.format, output_file=args.output)
