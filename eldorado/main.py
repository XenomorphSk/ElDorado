from flask import Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return "<h1>ElDorado — API de scraping online</h1>"
