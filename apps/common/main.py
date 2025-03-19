import uvicorn
# apps/common/main.py
if __name__ == "__main__":  
    uvicorn.run("app.api:app", host="127.0.0.1", port=4900, reload=True)