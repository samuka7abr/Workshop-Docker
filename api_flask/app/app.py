import json
import os

import psycopg2
import psycopg2.extras
import redis
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST", "postgres")
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ.get("DB_NAME", "workshop")
DB_USER = os.environ.get("DB_USER", "workshop")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "workshop")

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
CACHE_TTL = int(os.environ.get("CACHE_TTL", 60))

PORT = int(os.environ.get("PORT", 5000))

cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db():
    with get_db() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                done BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )


def invalidate_cache(task_id=None):
    cache.delete("tasks:all")
    if task_id is not None:
        cache.delete(f"tasks:{task_id}")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/tasks")
def list_tasks():
    cached = cache.get("tasks:all")
    if cached:
        return jsonify({"source": "cache", "data": json.loads(cached)})

    with get_db() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT id, title, description, done, created_at FROM tasks ORDER BY id;")
        rows = cur.fetchall()

    data = [
        {
            "id": r["id"],
            "title": r["title"],
            "description": r["description"],
            "done": r["done"],
            "created_at": r["created_at"].isoformat(),
        }
        for r in rows
    ]
    cache.setex("tasks:all", CACHE_TTL, json.dumps(data))
    return jsonify({"source": "db", "data": data})


@app.get("/tasks/<int:task_id>")
def get_task(task_id):
    key = f"tasks:{task_id}"
    cached = cache.get(key)
    if cached:
        return jsonify({"source": "cache", "data": json.loads(cached)})

    with get_db() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, title, description, done, created_at FROM tasks WHERE id = %s;",
            (task_id,),
        )
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "task not found"}), 404

    data = {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "done": row["done"],
        "created_at": row["created_at"].isoformat(),
    }
    cache.setex(key, CACHE_TTL, json.dumps(data))
    return jsonify({"source": "db", "data": data})


@app.post("/tasks")
def create_task():
    payload = request.get_json(silent=True) or {}
    title = payload.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400

    description = payload.get("description")
    done = bool(payload.get("done", False))

    with get_db() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tasks (title, description, done) VALUES (%s, %s, %s) RETURNING id;",
            (title, description, done),
        )
        new_id = cur.fetchone()[0]

    invalidate_cache()
    return jsonify({"id": new_id, "title": title, "description": description, "done": done}), 201


@app.put("/tasks/<int:task_id>")
def update_task(task_id):
    payload = request.get_json(silent=True) or {}
    fields = {k: payload[k] for k in ("title", "description", "done") if k in payload}
    if not fields:
        return jsonify({"error": "no fields to update"}), 400

    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [task_id]

    with get_db() as conn, conn.cursor() as cur:
        cur.execute(f"UPDATE tasks SET {set_clause} WHERE id = %s;", values)
        if cur.rowcount == 0:
            return jsonify({"error": "task not found"}), 404

    invalidate_cache(task_id)
    return jsonify({"id": task_id, **fields})


@app.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
        if cur.rowcount == 0:
            return jsonify({"error": "task not found"}), 404

    invalidate_cache(task_id)
    return "", 204


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=PORT)
