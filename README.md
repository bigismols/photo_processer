# photo_processer
Creative name, I know. This is my internship submission for HTX. I picked the Software Engineering task, where we need to program an API endpoint to process photos, more specifically captioning them with AI, creating thumbnails and extracting their metadata. 
# Project Overview
I used Flask to create this API endpoint, and Celery (a dependency of Flask) to run help manage the task queue. Currently, the endpoints allow users to upload images which will be processed on the API server. The backend will create thumbnails of small and medium size, caption the image with a Hugging Face model, and extract the length, width of the photo in pixels. It then stores the processed images locally in an sqlite3 database.

The following will be the contents of this document.
1. Setup and Installation
2. How to use photo_processor?
3. API Endpoints
4. Database Schema
5. Future Improvements

# 1. Setup and Installation
Before performing the setup, you need to have the following already installed:
- Python (be sure to update to the latest version)
- Pip (a python package manager, installed using python)
- Docker

The python downloads can be found in the [python official website](https://www.python.org/downloads/) and the installation steps for pip can be found in the [official pip documentation](https://pip.pypa.io/en/stable/installation/).  

For docker, you would need either Docker Desktop installed or docker installed in your Linux/MacOS machine. More details on the installation process can be found [here](https://docs.docker.com/engine/install/).

Now, follow the steps below to install the API. Steps below assumes user is on a Windows machine.

1. `cd path/to/your/project/folder`
2. `git clone https://github.com/bigismols/photo_processer.git`
3. Once in project folder,

For _Windows users_:

  - `py -3 -m venv .venv`
  - `.venv\Scripts\activate`

For _MacOS / Linux users_:  

  - `python3 -m venv .venv`
  - `. .venv/bin/activate`
5. `pip install -r requirements.txt`  

# 2. How to use photo_processor?

1. `.venv\Scripts\activate`
2. `celery -A flaskr.make_celery.celey worker --loglevel=INFO --include=flaskr.tasks.process_images`. This starts our celery worker
3. After making sure docker desktop is running, `docker run -d -p 5672:5672 rabbitmq` for **first time** starting the RabbitMQ server. In subsequent instances of using photo_processor, `docker start fervent_payne` (while still making sure docker is running in the background). `docker ps` to verify our container is running
4. `flask --app flaskr run --debug --host=127.0.0.1 --port=8000`
5. Server is up and running! Send requests with tool of your choice (Postman, curl etc.)

# 3. API Endpoints

## /api/images
Use case: Upload photos to be processsed (only .png and .jpg are allowed), and list all processed and processing photos  
Methods allowed: POST, GET

## /api/images/{id}
Use case: Gets the specific image detials, including URLs and thumbnails. id will be the name of the picture uploaded including the file extension  
Methods allowed: GET

## /api/images/{id}/thumbnail/{small, medium}
Use case: Returns the small and medium thumbnail for each of the two different endpoints. Medium size is of 320px by 320px and small is 100px by 100px  
Methods allowed: GET

## /api/stats
Use case: Returns processing statistics (average time to process, number of processed photos, number of processing photos)  
Methods allowed: GET

# 4. Database Schema
There is only 1 table in the database. The `image` table stores uploaded images, their metadata, processing status, and thumbnails.

| Column           | Type       | Description                                                                 |
|-----------------|-----------|-----------------------------------------------------------------------------|
| id              | INTEGER   | Primary key, auto-incremented.                                              |
| image_data      | BLOB      | Raw binary data of the original image.                                      |
| filename        | TEXT      | Name of the uploaded file.                                                  |
| mimetype        | TEXT      | MIME type of the image (e.g., `image/png`, `image/jpeg`).                   |
| length          | INTEGER   | Height of the image in pixels.                                              |
| width           | INTEGER   | Width of the image in pixels.                                               |
| thumbnail_small | BLOB      | Small thumbnail (128x128) of the image.                                     |
| thumbnail_medium| BLOB      | Medium thumbnail (320x320) of the image.                                    |
| caption         | TEXT      | Generated caption/description of the image using an AI model.              |
| created_at      | TIMESTAMP | Timestamp of when the image was uploaded (default: current timestamp).      |
| processed_at    | TIMESTAMP | Timestamp of when the image was processed (nullable until processed).       |
| status          | TEXT      | Processing status of the image (`processing` by default, `processed` when done). |

# 5. Future Improvements
- More rigorous testing
- Better error handling
  - More specific error messages
