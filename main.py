from fastapi import FastAPI, status, UploadFile, File
from fastapi.responses import JSONResponse
import os
import subprocess
import tempfile
import time

app = FastAPI()

start_time = time.time()

@app.get("/healthz")
async def health_check():
  uptime_seconds = time.time() - start_time
  env = os.environ.get('PY_ENV', 'development')
  return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={
      "message": "Service is healthy",
      "uptime": uptime_seconds,
      "environment": env
    }
  )

@app.post("/print")
async def print_document(file: UploadFile = File(...)):
  if not file:
    print("No file provided")
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={"message": "No file provided"}
    )
  
  if file.filename.endswith(".pdf") == False:
    print("Invalid file extension")
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={"message": "Invalid file extension. Only .pdf files are accepted."}
    )
    
  try:
    tmp_dir = os.path.join(os.getcwd(), "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    
    with tempfile.NamedTemporaryFile(dir=tmp_dir, suffix=f"_{file.filename}", delete=False) as temp_file:
      content = await file.read()
      temp_file.write(content)
      temp_file_path = temp_file.name
    
    if os.environ.get('PY_ENV') == 'production':
      subprocess.run(["lpr", temp_file_path])
    else:
      print("This is a development environment. Skipping actual print command...")
    print(f"File {file.filename} sent to printer")
  except Exception as e:
    print("Failed to print the document:", str(e))
    return JSONResponse(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      content={"message": f"Failed to print the document: {str(e)}"}
    )
  
  return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={"message": f"File {file.filename} sent to printer successfully"}
  )
