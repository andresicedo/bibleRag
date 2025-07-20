from flask import Flask
from src.main import create_app

application: Flask = create_app()

if __name__ == '__main__':
    application.run(port=8080, debug=True, use_reloader=False)