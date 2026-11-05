from flask import Flask, request, jsonify
from db import get_db, close_db, init_db

app = Flask(__name__)
app.teardown_appcontext(close_db)


def row_to_task(row):
    """Convert a psycopg2 RealDictRow into a clean JSON-friendly dict."""
    return {
        "id": row["id"],
        "title": row["title"],
        "author": row["author"],
        "published": row["published"],
        "created_at": row["created_at"].isoformat(),
    }

@app.route("/")
def index():
    return jsonify({"service": "first_flask_api", "endpoints": ["/books", "/books/<id>", "/stats"]})


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

    
# ---------- GET /books  (list all) ----------
@app.route("/books", methods=["GET"])
def get_books():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM books ORDER BY id")
        rows = cur.fetchall()
    return jsonify([row_to_task(r) for r in rows])


# ---------- GET /books/<id>  (get one) ----------
@app.route("/books/<int:book_id>", methods=["GET"])
def get_task(book_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        row = cur.fetchone()
    if row is None:
        return jsonify({"error": "Book with ID " + str(book_id) + " not found"}), 404
    return jsonify(row_to_task(row))  


# ---------- POST /books  (create) ----------
@app.route("/books", methods=["POST"])
def create_book():
    data = request.get_json(silent=True)
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO books (title, author, published) VALUES (%s, %s, %s) RETURNING *",
            (data["title"], data.get("author"), bool(data.get("published", False))),
        )
        row = cur.fetchone()
    db.commit()
    return jsonify(row_to_task(row)), 201


# ---------- PUT /books/<id>  (update) ----------
@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.get_json(silent=True) or {}
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        row = cur.fetchone()
        if row is None:
            return jsonify({"error": "Task with ID " + str(task_id) + " not found"}), 404

        new_title = data.get("title", row["title"])
        new_done = bool(data.get("done", row["done"]))

        cur.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *",
            (new_title, new_done, task_id),
        )
        updated = cur.fetchone()
    db.commit()
    return jsonify(row_to_task(updated))


# ---------- DELETE /tasks/<id>  (delete) ----------
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        deleted = cur.rowcount
    db.commit()

    if deleted == 0:
        return jsonify({"error": "Task not found"}), 404
    return "", 204


# ---------- BONUS: GET /tasks?done=true ----------
@app.route("/stats", methods=["GET"])
def stats():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS total, COUNT(*) FILTER (WHERE done) AS done FROM tasks")
        row = cur.fetchone()
    total = row["total"]
    done = row["done"]
    return jsonify({"total": total, "done": done, "pending": total - done})


if __name__ == "__main__":
    init_db()          
    app.run(debug=True)