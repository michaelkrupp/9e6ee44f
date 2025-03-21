import uvicorn


def main(*args, **kwargs):
    uvicorn.run(f"{__package__}:app", *args, **kwargs)
