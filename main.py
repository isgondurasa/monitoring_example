import os
import random
import time
from datetime import datetime

import requests
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram


app = Flask(__name__)
metrics = PrometheusMetrics(app)


ext_requests = Counter(
    "flask_http_ext_requests_path_total",
    "Ext request count by request path",
    ("path", "method", "status_code"),
)


ext_latency = Histogram(
    "flask_http_ext_requests_path_bucket",
    "Ext request latency",
    ("path", "method"),
)


def _call(path):
    url = os.environ.get("EXT_API_BASE_URL", "http://localhost:8082") + path
    response = None

    start = datetime.now()
    try:
        response = requests.get(url)
    finally:
        ext_requests.labels(
            path=path, method="GET", status_code=getattr(response, "status_code", 0)
        ).inc()
        delta = datetime.now() - start
        ext_latency.labels(path=path, method="GET").observe(delta.total_seconds())

    return response


@app.route("/api/v1/get200")
def get_200():
    time.sleep(random.random() * 0.2)
    return "ok", 200


@app.route("/api/v1/get400")
def get_400():
    time.sleep(random.random() * 0.4)
    return "ok", 400


@app.route("/api/v1/get500")
def get_500():
    time.sleep(random.random() * 0.5)
    return "ok", 500


@app.route("/api/v1/ext-get200")
def ext_get_200():
    path = "/api/v1/get200"
    response = _call(path)
    return "ok", response.status_code


@app.route("/api/v1/ext-get400")
def ext_get_400():
    path = "/api/v1/get400"
    response = _call(path)
    return "ok", response.status_code


@app.route("/api/v1/ext-get500")
def ext_get_500():
    path = "/api/v1/get500"
    response = _call(path)
    return "ok", response.status_code


metrics.register_default(
    metrics.counter(
        "flask_http_by_path_counter",
        "Request count by request paths",
        labels={
            "path": lambda: request.path,
            "method": lambda: request.method,
            "status": lambda r: r.status,
        },
    )
)


def run():
    app.run("0.0.0.0", os.environ.get("PORT", 6000))


if __name__ == "__main__":
    run()
