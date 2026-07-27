from flask import Flask
from flask_cors import CORS

from routes.dashboard import dashboard_bp
from routes.planner import planner_bp
from routes.progress import progress_bp

app = Flask(__name__)
CORS(app)

# Each page has its own file in routes/ — register them here.
app.register_blueprint(dashboard_bp)
app.register_blueprint(planner_bp)
app.register_blueprint(progress_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
