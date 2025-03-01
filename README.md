# High-Dimensional Image Processing System

#### This project is a FastAPI-based microservice for processing high-dimensional scientific images (e.g., 5D micros data or hyperspectral images). It provides endpoints for uploading images, extracting slices, performing PCA, calculating statistics, and more.

### Features

- Upload multi-dimensional TIFF images.

- Retrieve image metadata (dimensions, number of bands).

- Extract specific slices from the image (e.g., Z=5, Time=3, Channel=2).

- Perform Principal Component Analysis (PCA) for dimensionality reduction.

- Calculate basic image statistics (mean, standard deviation, min, max).

- Asynchronous processing for large images using Celery and Redis.


### Project Structure

```plaintext
Directory structure:
└── momenurmaruf2742-singularity_/
    ├── README.md
    ├── image_data.db
    ├── requirements.txt
    ├── .gitignore          
    ├── app/
    │   ├── __init__.py
    │   ├── celery.py
    │   ├── database.py
    │   ├── image_processor.py
    │   ├── main.py
    │   ├── models.py
    │   ├── schemas.py
    │   ├── tasks.py
    │   ├── utils.py
    │   └── __pycache__/
    ├── data/
    │   ├── at3_1m4_01.tiff
    │   ├── file_example_TIFF_10MB.tiff
    │   ├── invalid_file.txt
    │   ├── sample_5184×3456.tiff
    │   ├── sample_5184×3456f.tiff
    │   └── test.tiff
    ├── notebooks/
    │   └── demo.ipynb
    └── tests/
    │   ├── test_api.py
    │    └── __pycache__/
```
****Setup****

**Clone the repository:**

```
git clone https://github.com/your-username/high-dim-image-processor.git

cd high-dim-image-processor
```
Set up a virtual environment:




```
python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate

```
Install dependencies:
```
pip install -r requirements.txt
```
Start the FastAPI server:

```
uvicorn app.main:app --reload
```
Start the Celery worker (for asynchronous processing):

```
celery -A app.celery worker --loglevel=info
```
Start the Redis server (required for Celery):

```
redis-server
```

For Testing Use this command

```
pytest tests/test_image_processor.py 
```
## API Reference

#### Upload an Image

```http
  POST /upload
```

| Parameter | Type   | Description                |
|:----------|:-------| :------------------------- |
| `file`    | `file` | **Required** The image file to upload (must be a TIFF file).

#### Response
```
{

 "filename": "sample_5184×3456.tiff",

 "id": 1

}
```
#### Retrieve Image Metadata

```http
  GET /metadata/{image_id}
```
- Retrieves metadata for a specific image.

| Parameter | Type   | Description                |
|:----------|:-------| :------------------------- |
| `image_id`    | `integer` | **Required** ID of the image to fetch metadata for.|

#### Response
```
{

 "filename": "sample_5184×3456.tiff",

 "dimensions": "3456,5184,3",

 "num_bands": 3

}
```

#### Extract a Slice

```http
  GET /slice
```
- Extracts a specific slice from the image.

| Parameter         | Type     | Description                |
|:------------------|:---------| :------------------------- |
| `filename`        | `string` | **Required** Name of the image file.|
| `z`               | `integer` | **Optional** Z-index of the slice. |
| `channel`         | `integer` | **Optional** Channel index of the slice. |

#### Response
```
{

 "slice": [

   [187, 181, 179, ...],

   [174, 192, 177, ...],

   ...

 ]

}
```


#### Perform PCA

```http
  POST /analyze/{image_id}
```
- Performs Principal Component Analysis (PCA) on the image.

| Parameter     | Type     | Description                |
|:--------------|:---------| :------------------------- |
| `image_id`    | `integer`| **Required** ID of the image to analyze.|
| `operation`   | `string` | **Required** Operation to perform (e.g., "pca"). |

#### Response
```
{

 "task_id": "550e8400-e29b-41d4-a716-446655440000"

}

```


#### Retrieve Task Result

```http
  GET /task/{task_id}
```
- Retrieves the result of an asynchronous task (e.g., PCA).

| Parameter     | Type     | Description                |
|:--------------|:---------| :------------------------- |
| `task_id`    | `string`| **Required** ID of the task to fetch results for.|
| `operation`   | `string` | **Required** Operation to perform (e.g., "pca"). |

#### Response
```
{

 "status": "completed",

 "result": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], ...]

}

```


#### Calculate Image Statistics

```http
  GET /statistics
```
- Calculates basic image statistics (mean, standard deviation, min, max).

| Parameter     | Type     | Description                |
|:--------------|:---------| :------------------------- |
| `filename`    | `string`| **Required** Name of the image file.|
| `operation`   | `string` | **Required** Operation to perform (e.g., "pca"). |

#### Response
```

{

 "mean": [0.1, 0.2, 0.3],

 "std": [0.05, 0.06, 0.07],

 "min": [0.0, 0.0, 0.0],

 "max": [1.0, 1.0, 1.0]

}

```


### Example Usage

##### Upload an Image

```
curl -X POST "http://127.0.0.1:8000/upload" \

    -H "accept: application/json" \

    -H "Content-Type: multipart/form-data" \

    -F "file=@data/sample_5184×3456.tiff"
```
### Retrieve Metadata

```
curl -X GET "http://127.0.0.1:8000/metadata/1" \

    -H "accept: application/json"
```
### Extract a Slice

```
curl -X GET "http://127.0.0.1:8000/slice?filename=sample_5184×3456.tiff&channel=0" \

    -H "accept: application/json"
```

### Perform PCA
```
curl -X POST "http://127.0.0.1:8000/analyze/1?operation=pca" \

    -H "accept: application/json"
```
### Retrieve Task Result

```
curl -X GET "http://127.0.0.1:8000/task/550e8400-e29b-41d4-a716-446655440000" \

    -H "accept: application/json"
```
### Calculate Statistics

```
curl -X GET "http://127.0.0.1:8000/statistics?filename=sample_5184×3456.tiff" \

    -H "accept: application/json"
```
License

This project is licensed under the MIT License. See the LICENSE file for details.

Let me know if you need further assistance! 🚀
