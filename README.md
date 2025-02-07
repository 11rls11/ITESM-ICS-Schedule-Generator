# Generador de Horarios del ITESM en Formato ICS / ITESM ICS Format Schedule Generator

![Imagen de un Calendario Dibujo](readmeimg/calendario.png)

**Este script de Python interpreta el PDF** generado al terminar la inscripción **de** materias a través de la plataforma de inscripciones **IRIS** del Instituto Tecnológico y de Estudios Superiores de Monterrey, **con el objetivo de generar archivos** (*.ics*) **para importar fácilmente tus clases (semanas TEC, clases LiFE, Semanas de Etapa de Evaluación, Optativas, etc.) a** tu aplicación de calendario favorita (**Google Calendar, Outlook Calendar, iCal** *(sólo a tráves de Safari)*) **para facilitar la organización y planificación de tus clases**.

**This Python script parses the PDF generated after completing course enrollment through the** Instituto Tecnológico y de Estudios Superiores de Monterrey **IRIS class registration platform to generate** (*.ics*) **files for easily importing your classes** (TEC Weeks, LiFE classes, Evaluation Stage Weeks, General Education Classes, etc.) **into** your preferred calendar app (**Google Calendar, Outlook Calendar, iCal** *(only via Safari)*) **to stramline organizing and planning your class schedule**.

---

## Descripción / Description

![Ejemplo de horario](readmeimg/ejemplohorario.png)

### Español

El programa extrae información relevante del PDF de tu horario, como:

- **Nombre de las materias**
- **Nombre de los profesores**
- **Duración de las materias**
- **Fechas de duración de la clase** *(un período o más, saltando períodos vacacionales, días festivos y semanas TEC, sí la clase no es una semana TEC)*
- **Ubicaciones** *(Salones, Áreas, Remoto, etc.)*

Con esta información, crea eventos en formato iCalendar (.ics) que puedes importar en aplicaciones de calendario como Google Calendar, Outlook o el calendario de tu dispositivo móvil.

![Ejemplo Importación Todo](readmeimg/ejemploimportacion_Censurado.png)

![Ejemplo Importación Materia](readmeimg/ejemploimportacionmateria_Censurado.png)

### English

The program extracts relevant information from your schedule PDF, such as:

- **Courses names**
- **Professors names**
- **Classes length**
- **Class duration dates** *(a period or more, skipping vacational periods, holiday and TEC weeks, if the class is not a TEC Week)*
- **Locations** *(Classrooms, Areas, Remote/Online, etc.)*

Using this information, it creates events in iCalendar (.ics) format that you can import into calendar applications like Google Calendar, Outlook, or your mobile device's calendar.

---

## Características / Features

### Español

- **Conversión de todas las Materias en el PDF de tú horario**: **Con sólo ingresar el nombre del archivo *.pdf* generado por IRIS en Descargas, la fecha de consulta** *(actual por si quieres generar los archivos de las clases que te faltan, o igual o anterior a la fecha de inicio de semestre para generar los archivos de todas)* **y la fecha de inicio de semestre**, se muestran en consola todas las clases detectadas y **se generan automáticamente los archivos para importalos a tu app de calendario preferida**

- **Exclusión de semanas o días "especiales"**: Omite automáticamente las clases *no especiales* durante las semanas o días "especiales" (por ejemplo, semanas TEC, semanas 18, Semana Santa o días de asueto).

### English

- **Conversion of all courses in your PDF Schedule**: **By simply entering the filename of the *.pdf* generated by IRIS in Downloads, the query date** *(current date if you want to generate files for remaining classes, or equal to/prior to semester start date for all)***, and the semester start date**, all detected classes are displayed in the console and automatically generate importable files for your preferred calendar app.

- **Exclusion of "Special" Weeks/Days**: Automatically skips non-special classes during "special" periods (e.g., Tec Weeks, Week 18, Holy Week or Holidays). 

---

## Requisitos / Requirements

### Español

- **Python 3.6** *o una versión más reciente*
- **Bibliotecas Python**:
  - fitz (de la libreria PyMuPDF)
  - pytz
  - icalendar

### English

- **Python 3.6** *or newer*
- **Python Libraries**:
  - fitz (from the PyMuPDF library)
  - pytz
  - icalendar

---

## Uso / Usage

### Español

1. **Descarga e Instala Python en tu computadora** sí no lo tienes, puedes descargarlo [aquí](https://www.python.org/downloads/)

2. **Descarga el Archivo (*.zip*)**

[Descargando el .zip del repositorio](https://github.com/user-attachments/assets/5d1eb221-3b93-4775-b4bd-a444847f0f17)

3. **Descomprime y abre la carpeta con VSCode (Versión de Escritorio, NO Web)**

[Descomprimiendo la carpeta](https://github.com/user-attachments/assets/db3537b7-536f-427e-8340-b9d9fb61d3de)

[Abriendo la carpeta en VSCode](https://github.com/user-attachments/assets/6194c0d7-7275-4935-8d58-99d3d775e772)

4. **Instala la extensión de Python en VSCode** sí no las tienes.

[Instalando extensión de Python](https://github.com/user-attachments/assets/d7bc3fc2-3ee2-4fce-8e69-71fef822b91b)

5. **Abre una Terminal de Python e introduce el siguiente comando para instalar las dependencias necesarias para el programa:**

```bash
pip install PyMuPDF pytz icalendar
```

[Instalando dependencias](https://github.com/user-attachments/assets/3ab24faf-8db6-495a-a050-78e994670d65)

6. **Sí las dependencias no sé reconocen prueba cambiando tu Python Interpreter** sólo si tienes más de una versión de Python instalada

[Cambiando Interpreter](https://github.com/user-attachments/assets/89326322-23e5-4374-b22c-e296f667af74)

7. **Coloca el PDF de tu horario en la carpeta `Descargas` de tu usuario**, si no está ahí por defecto tras descargarlo a tráves de IRIS en tu navegador, si aún no lo has descargado, [descárgalo aquí](https://iris.tec.mx/app/enroll/schedule/saved).

[Descargando el horario](https://github.com/user-attachments/assets/2126f684-a14d-4f47-bf76-7c591bc15be7)

8. **Ejecuta el script introduciendo el siguiente comando en Terminal**:

```bash
python horarios.py
```

[Ejecutando el script en la terminal](https://github.com/user-attachments/assets/c509e876-5181-4a19-aef3-39fa2b886560)

9. **Sigue las instrucciones en pantalla**:

- Ingresa el nombre del archivo PDF sin la extensión `.pdf`(de manera predeterminada el `.pdf` de tu horario se llama `Resumen_proceso`, a excepción de que lo hayas descargado más de una vez o en más de una ocasión).
- Proporciona la fecha actual (o la que tú quieras, antes o durante de cualquier fecha del semestre) y la fecha de inicio del semestre en el formato solicitado (`YYYY-MM-DD` Año - Mes - Día).

[Generando los ics](https://github.com/user-attachments/assets/2121a304-cf81-4d05-b321-c5d175755dfc)

10. **Importa los archivos .ics generados**:

- Los archivos se guardarán en la carpeta `Horarios` (Sí no existe se creará) dentro de `Descargas`.
- Importa estos archivos en tu aplicación de calendario preferida.

[Importando los archivos ics a Google Calendar](https://github.com/user-attachments/assets/36f31486-de22-425d-b45b-90623e064f6c)

### English

1. **Download and Install Python** on your computer if you don't have it. Get it [here](https://www.python.org/downloads/).  

2. **Download the Repository (*.zip*)**  

3. **Unzip and open the folder in VSCode**  

4. **Install Python extensions in VSCode** if you don't have them.  

5. **Open a Python Terminal and run this command to install required dependencies:**

```bash
pip install PyMuPDF pytz icalendar
```

6. **If dependencies fail to install**, try switching your Python interpreter.  

7. **Place your schedule PDF in your user's `Downloads` folder**. If not already there after downloading via IRIS, [get it here](https://iris.tec.mx/app/enroll/schedule/saved).  

8. **Run the script with this terminal command**:  
```bash
python horarios.py
```

9. **Follow on-screen instructions**:  
- Enter PDF filename **without** `.pdf` extension (*default*: `Resumen_proceso` unless re-downloaded)  
- Provide current date (or any date before/during semester dates) and semester start date in `YYYY-MM-DD` format  

10. **Import generated .ics files**:  
- Files save to `Horarios` folder (auto-created if missing) within `Downloads`  
- Import these into your preferred calendar app. 

---

## Estructura del Proyecto / Project Structure

```
.
├── .gitignore
├── horarios.py
├── README.md
├── LICENSE
├── SECURITY.md
```

- **horarios.py**: Script principal para generar los archivos `.ics`. | Main script to generate the `.ics`. files.
- **README.md**: Este archivo. | This file.
- **LICENSE**: License de uso MIT | MIT's Use License
- **SECURITY.md**: Poliza de Seguridad | Security Policy

---

## Contribuciones / Contributions

### Español

¡Las contribuciones son bienvenidas! Por favor, abre un issue o un pull request para cualquier mejora o corrección.

### English

Contributions are welcome! Please open an issue or a pull request for any improvements or fixes.

---

## Licencia / License

### Español

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

### English

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Si tienes alguna otra pregunta o necesitas más ayuda, ¡no dudes en decírmelo!
---
Any doubts? I'm open to hear from you!
---
