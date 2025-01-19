from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'dwolt33'
app.config['MYSQL_DB'] = 'resume_screener'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


def compute_similarity(resume, job_description):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume, job_description])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])
    return similarity[0][0] * 100

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        resume_text = request.form.get('resume_text')
        job_description = request.form.get('job_description')

        if not user_name or not resume_text or not job_description:
            return "All fields are required!", 400

        
        match_score = compute_similarity(resume_text, job_description)

       
        try:
            cursor = mysql.connection.cursor()
            query = """
                INSERT INTO resumes (user_name, resume_text, job_description, match_score)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (user_name, resume_text, job_description, match_score))
            mysql.connection.commit()
            cursor.close()

            
            return render_template('result.html', match_score=match_score)
        except Exception as e:
            return f"An error occurred while saving data: {str(e)}"

    return render_template('upload.html')

@app.route('/results')
def results():
    match_score = request.args.get('match_score')  
    try:
        
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM resumes ORDER BY created_at DESC"
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        return render_template('results.html', match_score=match_score, results=results)
    except Exception as e:
        return f"An error occurred while retrieving data: {str(e)}"

@app.route('/test_db')
def test_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT DATABASE();')
        result = cursor.fetchone()
        cursor.close()
        return f"Connected to database: {result['DATABASE()']}"
    except Exception as e:
        return f"Database connection failed: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, port=5050)
