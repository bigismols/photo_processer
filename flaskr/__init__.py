import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from db import get_db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

    # Helper function to verify if file type is allowed
    def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # API endpoint to allow users to upload images
    # Need to store BLOB in DB and define route to get the BLOB for each image
    @app.route('/api/images', methods = ['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            if 'file' not in request.files:
                return jsonify({"error": "No file uploaded"}), 400
            file = request.files['file']
            if file and allowed_file(file.filename):
                # insert file saving to db logic here
                db = get_db()
                file_bytes = file.read()
                db.cursor.execute("INSERT INTO image (image_data) VALUES (?)" \
                           , (file_bytes))
                db.commit()
                return jsonify({'message': 'You have uploaded an image succesfully!'}), 201
        return jsonify({"error": "Invalid file type"}), 400

    # serve the images here
    @app.route('/api/images/<id>/<name>')
    def get_image(id, name):
        db = get_db()
        image_data = db.cursor.execute("SELECT image_data FROM images WHERE id=id")
        return jsonify({'message':'Data Downloaded'})

    from . import db
    db.init_app(app)

    return app