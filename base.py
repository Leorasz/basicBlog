from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = 'blog.db'

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit

def get_db():
    db = getattr(Flask, '_database', None)
    if db is None:
        db = Flask._database = sqlite3.connect(DATABASE, check_same_thread=False)
    else:
        try:
            # Try a simple command to check if the connection is still active
            db.execute('SELECT 1')
        except sqlite3.ProgrammingError:
            # If an error is raised, the connection is closed, so we reopen it
            db = Flask._database = sqlite3.connect(DATABASE, check_same_thread=False)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(Flask, "_database", None)
    if db:
        db.close()

@app.route("/")
def index():
    db = get_db()
    cursor2 = db.execute('SELECT id, announcement, created_at FROM announcements ORDER BY created_at DESC')
    cursor = db.execute('SELECT id, title, content, created_at FROM posts ORDER BY created_at DESC')
    posts = cursor.fetchall()
    announcements = cursor2.fetchall()
    print("This is index running")
    print(announcements)
    return render_template('index.html', posts=posts, announcements=announcements)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    print("You are viewing post")
    db = get_db()

    cursor = db.execute('SELECT id, title, content, created_at FROM posts ORDER BY created_at DESC')
    post = cursor.fetchone()

    if not post:
        return 'Post not found', 404

    return render_template('post.html', post=post)

@app.route('/announcement/<int:announcement_id>')
def view_announcement(announcement_id):
    print("You are viewing announcement")
    db = get_db()

    cursor = db.execute('SELECT id, announcement, created_at FROM announcements ORDER BY created_at DESC')
    announcement = cursor.fetchone()

    if not announcement:
        return 'Announcement not found', 404
    
    return render_template('announcement.html', announcement=announcement)

@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    print("new post being run")
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        db = get_db()

        db.execute('INSERT INTO posts (title, content) VALUES (?,?)', (title, content))

        db.commit()

        return redirect(url_for('index'))
    return render_template('new_post.html')

@app.route('/new_announcement', methods=['GET', 'POST'])
def new_announcement():
    print("new announcement being run")
    if request.method == 'POST':
        announcement = request.form['announcement']

        db = get_db()

        db.execute('INSERT INTO announcements (announcement) VALUES (?)', (announcement,))

        db.commit()

        return redirect(url_for('index'))
    return render_template('new_announcement.html')

init_db()
if __name__ == "__main__":
    app.run(debug=True, threaded=False)