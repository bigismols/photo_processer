import io
from PIL import Image
from flaskr import db, celery_app
from transformers import pipeline

@celery_app.task
def process_images(file_bytes, filename, mimetype):
    conn = db.get_db()
    file_bytes = file.read()
    pil_image = Image.open(file)
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

    conn.execute("""INSERT INTO image (image_data, filename, mimetype
                    , caption, length, width, thumbnail_small, thumbnail_medium) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """ 
                    , (file_bytes, filename, mimetype \
                , caption, length, width, thumbnail_small_bytes, thumbnail_medium_bytes))
    conn.commit()