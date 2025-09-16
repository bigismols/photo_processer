from datetime import datetime
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
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400
        # insert file saving to db logic her
        try:
            file_bytes = file.read()
            filename = file.filename
            mimetype = file.mimetype
            conn = db.get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO image (filename, mimetype, image_data, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (filename, mimetype, file_bytes, "processing", datetime.now().isoformat())
            )
            conn.commit()
            task = process_images.delay(file_bytes, filename, mimetype)
            return jsonify({'message': 'You have uploaded an image succesfully!'}), 201
        except Exception as e:
            return jsonify({'message': 'Unexpected server error!', 'details': str(e)}), 400
    elif request.method == 'GET':
        try:
            conn = db.get_db()
            cursor = conn.cursor()
            cursor.execute("""
                        SELECT filename, mimetype, caption, length
                        , width, processed_at, status FROM image
                        """)
            rows = cursor.fetchall()
            if not rows:
                return jsonify({"message": "There are no photos processed or being processed right now!"}), 201
            images = [
                {
                    "filename": row["filename"],
                    "mimetype": row["mimetype"],
                    "caption": row["caption"],
                    "length": row["length"],
                    "width": row["width"],
                    "url": f"/api/images/{row['filename']}",
                    "status": row["status"],
                    "processed_at": row["processed_at"],
                    "thumbnails": {
                        "small": f"/api/images/{row['filename']}/thumbnail/small",
                        "medium": f"/api/images/{row['filename']}/thumbnail/medium"
                    }
                }
                for row in rows
            ]
            return jsonify(images), 201
        except Exception as e:
            return jsonify({"error": "An unexpected error occured while fetching processed images", "details": str(e)}), 500
    else:
        return jsonify({'message': 'Method not allowed'}), 405

# serve the images here
@bp.route('/images/<name>')
def get_image(name):
    try:
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("""SELECT filename, mimetype, caption, length
                        , width, processed_at, status FROM image WHERE filename=?""", (name,))
        row = cursor.fetchone()
        if row is None:
            return jsonify({"error": "Image not found"}), 404
        return jsonify({
                "filename": row["filename"],
                "mimetype": row["mimetype"],
                "caption": row["caption"],
                "length": row["length"],
                "width": row["width"],
                "url": f"/api/images/{row['filename']}",
                "status": row["status"],
                "processed_at": row["processed_at"],
                "thumbnails": {
                    "small": f"/api/images/{row['filename']}/thumbnail/small",
                    "medium": f"/api/images/{row['filename']}/thumbnail/medium"
                    }
                }), 201
    except Exception as e:
        return jsonify({'message': 'Unexpected server error!', 'details': str(e)}), 400
    
@bp.route('/images/<name>/thumbnail/<size>')
def get_thumbnail(name, size):
    try:
        thumbnail_size = "thumbnail_" + size
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {thumbnail_size}, mimetype, filename FROM image WHERE filename=?", (name,))
        db_row = cursor.fetchone()
        if db_row is None:
            return jsonify({"error": "Image not found"}), 404
        return send_file(io.BytesIO(db_row[thumbnail_size]), mimetype=db_row['mimetype'] \
                            , download_name=db_row['filename'], as_attachment=True), 201
    except Exception as e:
        return jsonify({'message': 'Unexpected server error!', 'details': str(e)}), 400