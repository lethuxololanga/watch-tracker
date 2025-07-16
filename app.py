from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = 'tracker.db'

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                type TEXT,
                notes TEXT,
                trailer TEXT,
                watched INTEGER DEFAULT 0,
                added TEXT,
                rating INTEGER DEFAULT 3,
                priority TEXT DEFAULT 'Medium',
                price INTEGER DEFAULT 0,
                download_url TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER,
                name TEXT,
                email TEXT,
                requested_at TEXT
            )
        ''')

@app.route('/')
def index():
    filter_watched = request.args.get('filter', 'all')
    sort_by = request.args.get('sort', 'newest')

    query = "SELECT * FROM watchlist"
    if filter_watched == 'unwatched':
        query += " WHERE watched=0"

    query += " ORDER BY " + ("LOWER(title) ASC" if sort_by == 'alpha' else "added DESC")

    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.execute(query)
        movies = cur.fetchall()

    return render_template('index.html', movies=movies, filter=filter_watched, sort=sort_by)

@app.route('/add', methods=['POST'])
def add():
    data = request.form
    added = datetime.now().strftime("%Y-%m-%d %H:%M")
    with sqlite3.connect(DB) as conn:
        conn.execute("""INSERT INTO watchlist 
            (title, type, notes, trailer, rating, priority, added, price, download_url) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data['title'], data['type'], data['notes'], data['trailer'], int(data['rating']),
             data['priority'], added, int(data.get('price') or 0), data.get('download_url')))
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        data = request.form
        with sqlite3.connect(DB) as conn:
            conn.execute("""UPDATE watchlist SET
                title=?, type=?, notes=?, trailer=?, rating=?, priority=?, price=?, download_url=?
                WHERE id=?""",
                (data['title'], data['type'], data['notes'], data['trailer'],
                 int(data['rating']), data['priority'], int(data.get('price') or 0),
                 data.get('download_url'), id))
        return redirect(url_for('index'))
    with sqlite3.connect(DB) as conn:
        movie = conn.execute("SELECT * FROM watchlist WHERE id=?", (id,)).fetchone()
    return render_template('edit.html', movie=movie)

@app.route('/delete/<int:id>')
def delete(id):
    with sqlite3.connect(DB) as conn:
        conn.execute("DELETE FROM watchlist WHERE id=?", (id,))
    return redirect(url_for('index'))

@app.route('/toggle/<int:id>')
def toggle(id):
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        watched = cur.execute("SELECT watched FROM watchlist WHERE id=?", (id,)).fetchone()[0]
        conn.execute("UPDATE watchlist SET watched=? WHERE id=?", (0 if watched else 1, id))
    return redirect(url_for('index'))

@app.route('/request/<int:movie_id>', methods=['POST'])
def request_download(movie_id):
    name = request.form['name']
    email = request.form['email']
    requested_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    with sqlite3.connect(DB) as conn:
        conn.execute("""INSERT INTO requests (movie_id, name, email, requested_at)
                        VALUES (?, ?, ?, ?)""", (movie_id, name, email, requested_at))
    return redirect(url_for('index'))

@app.route('/requests')
def view_requests():
    with sqlite3.connect(DB) as conn:
        rows = conn.execute('''
            SELECT r.id, w.title, r.name, r.email, r.requested_at
            FROM requests r
            JOIN watchlist w ON r.movie_id = w.id
            ORDER BY r.requested_at DESC
        ''').fetchall()
    return render_template('requests.html', rows=rows)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
