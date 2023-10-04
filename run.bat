@echo off
setlocal enabledelayedexpansion

REM Parámetros con valores predeterminados
IF "%~1"=="" (SET QUERIES_FILE=.\queries.json) ELSE (SET QUERIES_FILE=%~1)
IF "%~2"=="" (SET ENV_FILE=.\.env) ELSE (SET ENV_FILE=%~2)
IF "%~3"=="" (SET OUTPUTS_DIR=.\outputs) ELSE (SET OUTPUTS_DIR=%~3)
IF "%~4"=="" (SET IMAGE_VERSION=v1) ELSE (SET IMAGE_VERSION=%~4)

REM Verificar cada parámetro y construir el comando Docker
SET DOCKER_CMD=docker run

IF "%QUERIES_FILE%"=="-" (SET QUERIES_FILE=.\queries.json)
for %%i in (%QUERIES_FILE%) do set ABS_QUERIES_FILE=%%~fi
SET DOCKER_CMD=!DOCKER_CMD! -v !ABS_QUERIES_FILE!:/src/queries.json


IF "%OUTPUTS_DIR%"=="-" (SET OUTPUTS_DIR=.\outputs)
for %%i in (%OUTPUTS_DIR%) do set ABS_OUTPUTS_DIR=%%~fi
SET DOCKER_CMD=!DOCKER_CMD! -v !ABS_OUTPUTS_DIR!:/src/outputs

@REM SET DOCKER_CMD=!DOCKER_CMD! --network mongo_default
SET DOCKER_CMD=!DOCKER_CMD! santosdev20/googlemapsscrapping:!IMAGE_VERSION!

echo !DOCKER_CMD!
%DOCKER_CMD%

endlocal
