from flask import Blueprint, render_template, request, redirect
import flask_app.views.my_module as my_module



data_bp = Blueprint('data', __name__)



@data_bp.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html')
