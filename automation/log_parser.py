import argparse
import re
from collections import Counter

LOG_REGEX = re.compile(
    r'(?P<ip>[\d\.]+) - - \[(?P<time>.*?)\] "(?P<request>.*?)" (?P<status>\d{3}) (?P<size>\d+) "(?P<referrer>.*?)" "(?P<user_agent>.*?)"'
)


def parse_log_file(filepath):
    ip_counter = Counter()
    status_counter = Counter()
    ua_counter = Counter()

    try:
        with open(filepath, "r") as f:
            for line in f:
                match = LOG_REGEX.match(line)
                if match:
                    data = match.groupdict()
                    ip_counter[data["ip"]] += 1
                    status_counter[data["status"]] += 1
                    ua_counter[data["user_agent"]] += 1
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

    return ip_counter, status_counter, ua_counter


def generate_html_report(
    ip_counter, status_counter, ua_counter, report_path="report.html"
):
    if ip_counter is None:
        return

    html = "<html><head><title>Log Analysis Report</title></head><body>"
    html += "<h1>Log Analysis Report</h1>"

    html += "<h2>Top 10 IP Addresses</h2><ol>"
    for ip, count in ip_counter.most_common(10):
        html += f"<li>{ip}: {count}</li>"
    html += "</ol>"

    html += "<h2>HTTP Status Codes</h2><ul>"
    for status, count in status_counter.items():
        html += f"<li>{status}: {count}</li>"
    html += "</ul>"

    html += "<h2>Top 10 User Agents</h2><ol>"
    for ua, count in ua_counter.most_common(10):
        html += f"<li>{ua}: {count}</li>"
    html += "</ol>"

    html += "</body></html>"

    try:
        with open(report_path, "w") as f:
            f.write(html)
        print(f"Report generated: {report_path}")
    except Exception as e:
        print(f"Error writing report: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse web server logs and generate a report."
    )
    parser.add_argument("logfile", help="Path to the log file (Apache/Nginx format).")
    parser.add_argument(
        "-o", "--output", default="report.html", help="Path for the output HTML report."
    )
    args = parser.parse_args()

    ip_counts, status_counts, ua_counts = parse_log_file(args.logfile)
    generate_html_report(ip_counts, status_counts, ua_counts, args.output)
