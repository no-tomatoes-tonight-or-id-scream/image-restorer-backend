# Image Restorer Backend

This is the backend for the Image Restorer project. It is a FastAPI application that uses Final2x-core to restore images.

## Project Structure

```bash
.
├── Final2x_core    # Main library of image-restore
│   ├── SRclass.py
│   ├── SRqueue.py
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   ├── config.yaml
│   └── util
├── Makefile
├── README.md
├── main.py         # FastAPI backend src
├── poetry.lock
├── pyproject.toml
├── tests           # Useful tests
│   ├── test.py
│   └── test_main.py
└── utils           # Useful utils that impl the backend
    ├── __init__.py
    └── processor.py
```

## Run

Make sure that you have `poetry` and `make` installed, then do `poetry install` at the root directory to install a subset of [Final2x-core](https://github.com/Tohrusky/Final2x-core). Then run `pip install fastapi uvicorn` to install our backend framework [FastAPI](https://fastapi.tiangolo.com/). Finally do `make run` and visit `http://localhost:8090/`, if everything works fine, your output is as follow:

```
{
    "message": "Welcome to the Image Restorer Backend",
    "status": "OK"
}
```

## APIs

- GET `/`: Root, only for test.
- POST `/process`: Upload an image and then start background image restoring process, with params `target_scale`, `pretrained_model_name` and `image`, return a `received` status and its `taskid`. 
- GET `/get_status`: With param `taskid`, check the task status, return a `status` in `processing`, `completed` or `error`. When returning an `error`, an error message can be unpack by getting value of `error`.
- GET `/get_result`: With param `taskid`, if completed then return restored image.
- GET `/get_model_list`: Return a dictionary of model list.

## Credits

- [Final2x-core](https://github.com/Tohrusky/Final2x-core)
- [ccrestoration](https://github.com/TensoRaws/ccrestoration)
