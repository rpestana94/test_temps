# test_temps

1. Para ejecutar el sdk primero se descomprime y se hacen ejecutables los siguientes archivos dentro de la carpeta de dji_thermal_sdk/utility/bin/linux/release_x64:

	- dji_ircm
	- dji_irp
	- dji_irp_omp

Esto se puede conseguir usando: chmod +x dji_ircm

El sdk se puede descargar desde: https://www.dji.com/mx/downloads/softwares/dji-thermal-sdk?backup_page=index&target=mx

2. Hay exportar donde se encuentran estos archivos y la carpeta de las librerias usando:

export DJI_DIRP_DIR="PATH_TO_DJI/dji_thermal_sdk/utility/bin/linux/release_x64"
export LD_LIBRARY_PATH="PATH_TO_DJI/dji_thermal_sdk/utility/bin/linux/release_x64:$LD_LIBRARY_PATH"

Esto se hace en la consola donde se ejecutar el comando para obtener la imagen raw, tambien se pueden agregar al archivo bashrc y reiniciar la consola

3. Para convertir una imagen de jpg a raw se usa:

PATH_TO_DJI/dji_thermal_sdk/utility/bin/linux/release_x64/dji_irp -s PATH_TO_IMAGEN -a measure -o ARCHIVO.raw --measurefmt float32

4. Usar la imagen raw dentro del codigo python temp_roi.py, reemplazar linea 6 por el path de la imagen raw
