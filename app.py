from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('botauswählen.html')

@app.route('/redirected')
def redirected():
    return '<h1>Du wurdest weitergeleitet!</h1>'

if __name__ == '__main__':
    app.run(debug=True)
