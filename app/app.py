import os
import time
import asyncio
import redis
import boto3
import psycopg2
import pymongo
from fastapi import FastAPI
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from threading import Thread
from pydantic import BaseModel

app = FastAPI(title="infra-tester", version="0.0.1")

# --- Prometheus metrics ---
metric_up = Gauge("infra_service_up", "Service up status", ["service"])
metric_duration = Gauge("infra_check_duration_seconds", "Duration of last check")

# --- Configuration ---
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "5"))  # seconds


class CheckResult(BaseModel):
    service: str
    ok: bool
    message: str


def check_postgres():
    url = os.getenv("POSTGRES_URL")
    if not url:
        return CheckResult(service="postgres", ok=False, message="POSTGRES_URL not set")
    try:
        conn = psycopg2.connect(url, connect_timeout=3)
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        conn.close()
        return CheckResult(service="postgres", ok=True, message="OK")
    except Exception as e:
        return CheckResult(service="postgres", ok=False, message=str(e))


def check_mongo():
    url = os.getenv("MONGO_URL")
    if not url:
        return CheckResult(service="mongo", ok=False, message="MONGO_URL not set")
    try:
        client = pymongo.MongoClient(url, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        return CheckResult(service="mongo", ok=True, message="OK")
    except Exception as e:
        return CheckResult(service="mongo", ok=False, message=str(e))


def check_redis():
    url = os.getenv("REDIS_URL")
    if not url:
        return CheckResult(service="redis", ok=False, message="REDIS_URL not set")
    try:
        r = redis.from_url(url)
        r.ping()
        return CheckResult(service="redis", ok=True, message="OK")
    except Exception as e:
        return CheckResult(service="redis", ok=False, message=str(e))


def check_s3():
    endpoint = os.getenv("S3_ENDPOINT")
    key = os.getenv("S3_ACCESS_KEY")
    secret = os.getenv("S3_SECRET_KEY")
    if not (endpoint and key and secret):
        return CheckResult(service="s3", ok=False, message="Missing envs")
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=key,
            aws_secret_access_key=secret,
        )
        s3.list_buckets()
        return CheckResult(service="s3", ok=True, message="OK")
    except Exception as e:
        return CheckResult(service="s3", ok=False, message=str(e))


def perform_checks():
    start = time.time()
    services = [check_postgres(), check_mongo(), check_redis(), check_s3()]
    duration = round(time.time() - start, 3)

    # Update metrics
    for s in services:
        metric_up.labels(service=s.service).set(1 if s.ok else 0)
    metric_duration.set(duration)

    return {"duration": duration, "results": [s.dict() for s in services]}


# --- Background check loop ---
async def periodic_checker():
    while True:
        perform_checks()
        await asyncio.sleep(CHECK_INTERVAL)


@app.on_event("startup")
async def startup_event():
    Thread(target=lambda: asyncio.run(periodic_checker()), daemon=True).start()


# --- HTTP routes ---
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/check")
def manual_check():
    result = perform_checks()
    result["status"] = "ok" if all(r["ok"] for r in result["results"]) else "fail"
    return result


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
