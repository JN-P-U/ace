import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.apis:app", host="127.0.0.1", port=4900, reload=True)
