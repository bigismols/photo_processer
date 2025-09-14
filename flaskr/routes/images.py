import io
from flask import request, jsonify, send_file, Blueprint
from flaskr import db
from transformers import pipeline
from flaskr.tasks.process_images import process_images

bp = Blueprint('images', __name__, url_prefix='/api')

ALLOWED_EXTENSIONS = {'png', 'jpg'}

# Helper function to verify if file type is allowed
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# API endpoint to allow users to upload images
# Need to store BLOB in DB and define route to get the BLOB for each image
# Now we will try 
@bp.route('/images', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files['file']
        if not file or not allowed_file(file.filename): 
            return jsonify({"error": "Invalid file type"}), 400
        # insert file saving to db logic her
        try:
            file_bytes = file.read()
            filename = file.filename
            mimetype = file.mimetype
            task = process_images.delay(file_bytes, filename, mimetype)
            return jsonify({'message': 'You have uploaded an image succesfully!'}), 201
        except Exception as e:
            return jsonify({'message': 'Unexpected server error!', 'details': str(e)}), 400
    else:
        return jsonify({'message': 'Method not allowed'}), 405

# serve the images here
@bp.route('/images/<name>')
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
    
@bp.route('/images/<name>/<thumbnail_size>')
def get_thumbnail(name, thumbnail_size):
    try:
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {thumbnail_size}, mimetype, filename FROM image WHERE filename=?", (name,))
        db_row = cursor.fetchone()
        if db_row is None:
            return jsonify({"error": "Image not found"}), 404
        return send_file(io.BytesIO(db_row[thumbnail_size]), mimetype=db_row['mimetype'] \
                            , download_name=db_row['filename'], as_attachment=True)
    except Exception as e:
        return jsonify({'message': 'Unexpected server error!', 'details': str(e)}), 400