import os
import io
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flaskr import db

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

    from . import db
    db.init_app(app)

    with app.app_context():
        db.init_db()

    ALLOWED_EXTENSIONS = {'png', 'jpg'}

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
            if not file or not allowed_file(file.filename): 
                return jsonify({"error": "Invalid file type"}), 400
            # insert file saving to db logic here
            try:
                conn = db.get_db()
                file_bytes = file.read()
                conn.execute("INSERT INTO image (image_data, filename, mimetype) VALUES (?, ?, ?)" \
                            , (file_bytes, file.filename, file.mimetype))
                conn.commit()
                return jsonify({'message': 'You have uploaded an image succesfully!'}), 201
            except Exception as e:
                return jsonify({'message': 'Unexpected server error!', 'details': str(e)}), 400

    # serve the images here
    @app.route('/api/images/<name>')
    def get_image(name):
        try:
            conn = db.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT image_data, mimetype, filename FROM image WHERE filename=?", (name,))
            db_row = cursor.fetchone()
            if db_row is None:
                return jsonify({"error": "Image not found"}), 404
            return send_file(io.BytesIO(db_row['image_data']), mimetype=db_row['mimetype'] \
                             , download_name=db_row['filename'], as_attachment=True)
        except Exception as e:
            return jsonify({'message': 'Unexpected server error!', 'details': str(e)}), 400

    return app