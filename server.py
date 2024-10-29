from flask import Flask, send_from_directory
from flask_cors import CORS
from App import app as flask_app

app = Flask(__name__, static_folder='.')
CORS(app)

# Serve static files
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# Mount the Flask app routes from App.py
app.add_url_rule('/calculate', 'calculate', flask_app.view_functions['calculate'], methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True, port=8000)
