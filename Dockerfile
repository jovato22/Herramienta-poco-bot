# 1. Usamos la imagen oficial de Python 3.10
FROM python:3.10-slim

# 2. Establecemos el directorio de trabajo
WORKDIR /app

# 3. Copiamos el archivo de librerías primero
COPY requirements.txt .

# 4. Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos todo tu código al contenedor
COPY . .

# 6. El comando para arrancar (IMPORTANTE: Cambia 'main.py' por tu archivo)
CMD ["python", "main.py"]
