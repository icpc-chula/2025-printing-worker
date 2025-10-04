#!/bin/bash

PORT=8081
PY_ENV=development

PY_ENV=${PY_ENV} uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}