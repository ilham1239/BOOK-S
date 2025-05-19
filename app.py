from flask import Flask, request, session, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    # users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL)''')
    # books table
    c.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        content TEXT NOT NULL)''')
    # add default admin user if not exists
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES ('admin', 'adminpass')")
    # add some sample books if empty
    c.execute("SELECT * FROM books")
    if not c.fetchone():
        c.execute("INSERT INTO books (title, author, content) VALUES (?, ?, ?)", 
                  ("Pride and Prejudice", "Jane Austen", "Content of Pride and Prejudice..."))
        c.execute("INSERT INTO books (title, author, content) VALUES (?, ?, ?)", 
                  ("1984", "George Orwell", "Content of 1984..."))
        c.execute("INSERT INTO books (title, author, content) VALUES (?, ?, ?)", 
                  ("To Kill a Mockingbird", "Harper Lee", "Content of To Kill a Mockingbird..."))
    conn.commit()
    conn.close()

init_db()

# vulnerable login route with SQL injection risk
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('books.db')
        cursor = conn.cursor()
        # WARNING: SQL Injection vulnerability here
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print(f"Executing query: {query}")
        try:
            cursor.execute(query)
            user = cursor.fetchone()
        except Exception as e:
            conn.close()
            return f"<p>Error in query: {e}</p>"
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template_string(login_template, error="Invalid credentials")
    return render_template_string(login_template)

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('books_injection.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, author FROM books")
    books = cursor.fetchall()
    conn.close()
    return render_template_string(home_template, username=session['username'], books=books)

@app.route('/book/<int:book_id>')
def book(book_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('books_injection.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title, author, content FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    conn.close()
    if not book:
        return "<h3>Book not found!</h3><a href='/'>Back</a>"
    return render_template_string(book_template, title=book[0], author=book[1], content=book[2])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


login_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
<head>
  <title>BOOK'S</title> 
</head>
    <title>Login</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        form {
            background: #fff;
            padding: 30px 40px;
            border-radius: 12px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            width: 320px;
        }
        input {
            padding: 12px;
            margin: 10px 0;
            width: 100%;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-sizing: border-box;
            transition: 0.3s;
        }
        input:focus {
            border-color: #764ba2;
            outline: none;
        }
        input[type="submit"] {
            background: #764ba2;
            color: white;
            font-weight: bold;
            cursor: pointer;
            border: none;
        }
        input[type="submit"]:hover {
            background: #5a2a83;
        }
        h2 {
            text-align: center;
            color: #764ba2;
            margin-bottom: 20px;
        }
        p.error {
            color: red;
            text-align: center;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <form method="post">
        <h2>Login</h2>
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
        <label>Username:</label>
        <input name="username" autocomplete="off" />
        <label>Password:</label>
        <input name="password" type="password" autocomplete="off" />
        <input type="submit" value="Login" />
    </form>
</body>
</html>

'''

home_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Books</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #f0f2f5;
            padding: 40px;
        }
        h1 {
            color: #764ba2;
        }
        h3 {
            color: #444;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            margin: 12px 0;
            font-size: 18px;
        }
        a {
            color: #5a2a83;
            text-decoration: none;
            font-weight: bold;
        }
        a:hover {
            text-decoration: underline;
        }
        .logout {
            margin-top: 30px;
            display: inline-block;
            padding: 10px 20px;
            background: #764ba2;
            color: white;
            border-radius: 6px;
            text-decoration: none;
            transition: 0.3s;
        }
        .logout:hover {
            background: #5a2a83;
        }
    </style>
</head>
<body>
    <h1>Welcome</h1>
    <h3>Available Books:</h3>
    <ul>
    {% for id, title, author in books %}
        <li><a href="{{ url_for('book', book_id=id) }}">{{ title }}</a> by {{ author }}</li>
    {% endfor %}
    </ul>
    <a href="{{ url_for('logout') }}" class="logout">Logout</a>
</body>
</html>

'''

book_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{ title }}</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #ffffff;
            padding: 40px;
            max-width: 800px;
            margin: auto;
            line-height: 1.7;
            color: #333;
        }
        h1 {
            color: #764ba2;
            margin-bottom: 10px;
        }
        h3 {
            color: #666;
            margin-bottom: 20px;
        }
        p {
            font-size: 17px;
            margin-bottom: 16px;
        }
        a {
            margin-top: 20px;
            display: inline-block;
            color: #5a2a83;
            text-decoration: none;
            font-weight: bold;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <h3>Author: {{ author }}</h3>
    <p>Orgueil et Préjugés (Pride and Prejudice) est un roman de la femme de lettres anglaise Jane Austen paru en 1813. Il est considéré comme l'une de ses œuvres les plus significatives et est aussi la plus connue du grand public.</p>
    <p>The news that a wealthy young gentleman named Charles Bingley has rented the manor of Netherfield Park causes a great stir in the nearby village of Longbourn, especially in the Bennet household...</p>
    <a href="{{ url_for('home') }}">Back to Books</a>
</body>
</html>

'''

if __name__ == '__main__':
    app.run(debug=True)