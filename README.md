
# Tournament

Sistema de gestión de eventos deportivos


## Configuración del proyecto

Crear un entorno virtual 
```bash
python -m venv .venv
```
Activar el entorno virtual
```bash
.venv\Scripts\activate
```
Instalar las dependencias necesarias
```bash
pip install -r requirements.txt
```
Crear la base de datos 'tournament_db'
```bash
CREATE DATABASE tournament_db;
```
En el archivo config.py establecer la contraseña del usuario root de tu MySQL
```bash
DEFAULT_MYSQL_ROOT_PASSWORD = "root_password"
```

    
## Ejecución del proyecto

Una vez realizada la configuración anterior, teniendo el entorno virtual activado ejecutar el archivo app.py

```bash
python app.py
```

