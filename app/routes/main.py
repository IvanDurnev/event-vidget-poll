from flask import Blueprint, redirect

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
def index():
    return redirect('/poll')