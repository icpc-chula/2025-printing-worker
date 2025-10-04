from fastapi import FastAPI, status, UploadFile, File
from fastapi.responses import JSONResponse
import os
import subprocess
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
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={"message": "No file provided"}
    )
  
  if file.content_type != "application/pdf":
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={"message": "Invalid file type. Only PDF files are accepted."}
    )
  
  if file.filename.endswith(".pdf") == False:
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={"message": "Invalid file extension. Only .pdf files are accepted."}
    )
    
  try:
    with open(f"/tmp/{file.filename}", "wb") as temp_file:
      content = await file.read()
      temp_file.write(content)
    
    if os.getEnv():
      subprocess.run(["lpr", f"/tmp/{file.filename}"])
    else:
      print("This is a development environment. Skipping actual print command...")
    print(f"File {file.filename} sent to printer")
  except Exception as e:
    return JSONResponse(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      content={"message": f"Failed to print the document: {str(e)}"}
    )
  finally:
    try:
      subprocess.run(["rm", f"/tmp/{file.filename}"])
    except Exception as e:
      pass
  
  return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={"message": f"File {file.filename} sent to printer successfully"}
  )