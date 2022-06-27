from flask import Flask

def create_app():
    
    app = Flask(__name__)

    from flask_app.views.a_main_views import main_bp
    app.register_blueprint(main_bp)
    from flask_app.views.b_hungry_views import hungry_bp
    app.register_blueprint(hungry_bp)
    from flask_app.views.c_data_views import data_bp
    app.register_blueprint(data_bp)

    return app
    