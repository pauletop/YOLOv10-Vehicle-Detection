from flask import Flask, request, render_template
import cv2
import numpy as np

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'my@secret#Key'

    from .views import views
    app.register_blueprint(views)

    return app