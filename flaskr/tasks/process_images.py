from datetime import datetime
import io
from flaskr import db, celery_app
from PIL import Image
from transformers import pipeline

@celery_app.task(name="flaskr.tasks.process_images.process_images")
def process_images(file_bytes, filename, mimetype):
    processed_at = datetime.now().isoformat()
    conn = db.get_db()
    pil_image = Image.open(io.BytesIO(file_bytes))
    length = pil_image.size[1]
    width = pil_image.size[0]
    captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large")
    caption = captioner(pil_image)[0]['generated_text']
    thumbnail_small = pil_image.copy()
    thumbnail_small_bytes = io.BytesIO()
    thumbnail_medium = pil_image.copy()
    thumbnail_medium_bytes = io.BytesIO()
    # processing small thumbnail
    thumbnail_small.thumbnail((128, 128))
    thumbnail_small.save(thumbnail_small_bytes, format=mimetype.split("/")[1])
    thumbnail_small_bytes = thumbnail_small_bytes.getvalue()
    # processing medium thumbnail
    thumbnail_medium.thumbnail((320, 320))
    thumbnail_medium.save(thumbnail_medium_bytes, format=mimetype.split("/")[1])
    thumbnail_medium_bytes = thumbnail_medium_bytes.getvalue()

    conn.execute("""
        UPDATE image
        SET caption=?, length=?, width=?, thumbnail_small=?, thumbnail_medium=?, processed_at=?, status=?
        WHERE filename=?
        """, (caption, length, width, thumbnail_small_bytes, thumbnail_medium_bytes
              , processed_at, "processed", filename))
    conn.commit()
    print("DONE WITH PROCESSING")