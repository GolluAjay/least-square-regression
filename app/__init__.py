from flask import Flask
from flask_socketio import SocketIO

# Initialize SocketIO globally
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize SocketIO with the app
    socketio.init_app(app)

    with app.app_context():
        # Register the blueprint here
        from .routes import routes
        app.register_blueprint(routes)

    return app

# Function to run the app with socketio
if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True)  # Use socketio.run instead of app.run
