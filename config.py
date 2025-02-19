import os

class Config:
    SECRET_KEY = 'supersecretkey'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')

    @staticmethod
    def init_app(app):
        app.config['SECRET_KEY'] = Config.SECRET_KEY
        app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
