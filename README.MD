# Sistema de inventario TIT Empresarial
<p>
Lenguajes y Bibliotecas utilizadas
</p>

- Python 3.13.9
- Flask 3.1.1
- Werkzeug 3.1.3
- mysql-connector-python 9.3.0
- weasyprint 66.0
#Descarga e instalación del Proyecto

**Nota:** Debemos tener instalado la version correspondiente de python

1. Primero iremos a el repositorio y Daremos en **Code** y **Download Zip** https://github.com/Luis020701/PracticasProf.git
![Descargar](https://i.postimg.cc/5tC87cfZ/Descargar.png)

2. Extraemos el Archivo y nos dejara una carpeta
![Extraer](https://i.postimg.cc/jjfJ6GTn/extraer-1.gif)

3. Nos pocisionamos dentro de la carpeta
![Extraer](https://i.postimg.cc/QdTk2xPp/Carpeta.png)

4. Damos clic derecho y **Abrir en Terminal**
![MenuContextual](https://i.postimg.cc/ZqDfmDjt/Terminal.png)

5. Nos abrira Windows Power Shell, en la terminal escribiremos **CMD**

6. Una vez cambiamos a cmd Escribiremos el siguiente Comando para activar el entorno virtual (Necesario para no entrar en conflictos con las librerias)
```
python3 -m venv .venv
```
**Nota:** El comando anterior sirve para crear el entorno virtual, *.venv* es el nombre del entorno, lo puedes cambiar a tu gusto

7. Una vez creado procederemos a activar el entorno con el siguiente comando:
```
.venv\Scripts\activate
```
8. Ya activo instalamos todas las librerias:

Instalar *flask*
```
pip install flask 
```
Instalar *Werkzeug*
```
pip install Werkzeug
```
instalar *mysql-connector-python*
```
pip install mysql-connector-python
```
instalar *weasyprint*
```
pip install weasyprint
```
**Nota:** Si se usara en Windows se necesitara instalar un paquete llamado  *GTK3 Runtime*

9. Para instalar *GTK3 Runtime* abriremos el siguiente link: https://www.msys2.org/

10. Escogemos el necesario para nuestra arquitectura
![GTK](https://i.postimg.cc/Kzxtd7S3/GTK.png)

11. Vamos a descargas y al abrir el archivo nos saldra algo asi
![SetUp](https://i.postimg.cc/mrRcDbXg/Set-Up-GTK.png)

12. Damos **next**
13. Escogemos la ruta de instalacion(**Nota:** Si tenemos mas de un disco procuraremos escoger en el que instalamos python)
![Ruta](https://i.postimg.cc/ZY16mhSz/2GTK.png)
14. Una vez finalizado nos saldra algo asi que nos indica que todo se instalo correctamente (Dejamos pulsado *RUN MSYS2 now*):
![Finish](https://i.postimg.cc/Zq25N4jv/install-3-finish.png)

15. Se abrira la consola de comandos
![Terminal](https://i.postimg.cc/CKqVWDHz/install-4-terminal.png)

**Nota:** Para poder usar *Weasyprint* necesitamos usar la libreria *Pango* con sus dependencias para poder renderizar texto, que en este caso se usa para la generacion de *PDF'S* 
16. En la consola de comandos de *GTK* escribiremos el siguiente comando:
```
pacman -S mingw-w64-x86_64-pango
```
Una vez hecho todo lo anterior para poder ejecutar el proyecto nos iremos a la carpeta de este mismo y ejecutaremos el siguiente comando:
```
python  .\src\index.py
```
El comando anterior se ejecuta con el entorno previamente activado, sabremos que esta activado checando la ruta de la carpeta en la terminal:
![Activacion](https://i.postimg.cc/vZmnL87J/Activar.png)

Al inicio de la ruta comos saldra el nombre del entorno

17. Al ejecutar el comando anterior nos dara la direccion en la cual podremos visualizar el Inventario

![Ejecucion](https://i.postimg.cc/FR6Cmnrz/Ejecucion.png)
(**Nota**: )

![LoginInventario](https://i.postimg.cc/1R2RYmZj/Login.png)

¡Gracias por su atencion y confianza y a disfrutar del proyecto!