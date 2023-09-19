

# Google Maps Scraper

El propósito de este proyecto es automatizar la extracción de información específica de
Google Maps. Durante la primera fase, se desarrolla un proyecto en Python que toma
instrucciones sobre las zonas y las consultas que debe realizar. Posteriormente, extrae la
información requerida y la almacena en una base de datos MongoDB. Finalmente, se
genera un archivo Excel con el formato específico solicitado

## Pasos para usar el proyecto:

### 1. Obtener la imagen de Docker:

Para obtener la imagen de Docker, primero debes hacer login a Docker Hub:

```bash
docker login
```

Usa las siguientes credenciales:

- **Username**: `santosdev20`
- **Password**: `[Tu contraseña]` 

### 2. Crear archivos de configuración:

Antes de ejecutar el proyecto, es necesario crear dos archivos: `queries.json` y `.env`.

**`queries.json`**:

Este archivo define las consultas de localizaciones para el scraper. Debe tener el siguiente formato:

```json
[
    {
        "name": "PENNSYLVANIA",
        "countries": [
            {
                "name": "JEFFERSON COUNTY",
                "zips": [
                    19140
                ]
            }
        ]
    }
]
```

El archivo consiste en una lista de estados, cada estado tiene sus países y cada país tiene sus códigos postales (zipcodes).

**`.env`**:

Este archivo contiene las variables de entorno que necesita el scraper. A continuación se presentan las variables requeridas:

```
CONTACTACTS_DB=contacts_database
CONTACTS_COLLECTION=contacts
LINKS_COLLECTION=links
INDUSTRIES_COLLECTION=industries
SYNC_M_COLLECTION=sync_collection
MONGO_CONNECTION=mongodb://root:example@mongo_mongo_1:27017
ENVIRONMENT=prod
```
la variable mongo conection debe ir con la cadena de conexion a la base de datos productiva.


### 3. Correr el proyecto:

Para ejecutar el proyecto, primero da permisos de ejecución al script:

```bash
chmod +x run.sh   # Para Linux
```

Luego, ejecuta el script correspondiente:

```bash
./run.sh  [queriespath] [env path] [outputspath] [version]         # Para Linux
```
o
```bash
./run.bat [queriespath] [env path] [outputspath] [version]         # Para Windows
```

Por ejemplo 

```bash
./run.sh ./queriesExample.json .envExample ./outputs v1
# Estoy pasando el archivo queriesExample.json con la informacion de las zonas que quiero cubrir
# los archivos de excel quedaran en la carpeta outputs
# Estoy pasandole el archivo .envExample con las variables de entorno
# Estoy usando la v1 del proyecto.
```

El proyecto empezara a correr y mostrara logs de todo lo que esta haciendo, al final en la carpeta outputs estaran todos los excels generados
