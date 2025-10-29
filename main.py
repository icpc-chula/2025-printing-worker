from fastapi import FastAPI, status, UploadFile, File, Body
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
      result = subprocess.run(["lpr", temp_file_path], capture_output=True, text=True)
      if result.returncode != 0:
        raise Exception(f"Print command failed: {result.stderr}")
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

@app.post("/print/manual")
async def manual_print(data: dict = Body(...)):
  filename = data.get("filename")
  if not filename:
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={"message": "filename is required in JSON body"}
    )
  try:
    tmp_dir = os.path.join(os.getcwd(), "tmp")
    
    matching_files = [f for f in os.listdir(tmp_dir) if f.endswith(f"_{filename}")]
    
    if not matching_files:
      return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": f"No file found ending with '{filename}' in tmp directory"}
      )
    
    if len(matching_files) > 1:
      return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": f"Multiple files found ending with '{filename}': {matching_files}"}
      )
    
    file_path = os.path.join(tmp_dir, matching_files[0])
    
    if os.environ.get('PY_ENV') == 'production':
      result = subprocess.run(["lpr", file_path], capture_output=True, text=True)
      if result.returncode != 0:
        raise Exception(f"Print command failed: {result.stderr}")
    else:
      print("This is a development environment. Skipping actual print command...")
    
    print(f"Manually printed file: {matching_files[0]}")
    return JSONResponse(
      status_code=status.HTTP_200_OK,
      content={"message": f"File {filename} sent to printer successfully"}
    )
    
  except Exception as e:
    print("Failed to manually print the document:", str(e))
    return JSONResponse(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      content={"message": f"Failed to manually print the document: {str(e)}"}
    )