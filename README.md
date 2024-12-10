# Generador de Horarios del ITESM en Formato ICS / ITESM ICS Format Schedule Generator

Este script en Python interpreta el PDF generado al terminar la inscripción de materias a través de la plataforma de inscripciones del Instituto Tecnológico y de Estudios Superiores de Monterrey (IRIS) con el objetivo de generar archivos de calendario (.ics) para facilitar la organización y planificación de tus clases en tu aplicación de calendario preferida.

This Python script parses the PDF generated after completing course enrollment through the Instituto Tecnológico y de Estudios Superiores de Monterrey (IRIS) platform with the goal of generating calendar files (.ics) to facilitate the organization and planning of your classes in your preferred calendar app.

---

## Descripción / Description

### Español

El programa extrae información relevante del PDF de tu horario, como:

- **Materias**
- **Profesores**
- **Horarios**
- **Fechas**
- **Ubicaciones**

Con esta información, crea eventos en formato iCalendar (.ics) que puedes importar en aplicaciones de calendario como Google Calendar, Outlook o el calendario de tu dispositivo móvil.

### English

The program extracts relevant information from your schedule PDF, such as:

- **Courses**
- **Professors**
- **Schedules**
- **Dates**
- **Locations**

Using this information, it creates events in iCalendar (.ics) format that you can import into calendar applications like Google Calendar, Outlook, or your mobile device's calendar.

---

## Características / Features

### Español

- **Análisis automático del PDF de horario**: No necesitas ingresar manualmente tus clases; el script extrae toda la información necesaria del PDF.
- **Generación de archivos .ics**: Crea archivos de calendario compatibles con la mayoría de las aplicaciones de calendario.
- **Exclusión de semanas específicas**: Omite automáticamente las clases durante las semanas designadas para actividades especiales (por ejemplo, semanas 6, 12 y 18).
- **Soporte para clases especiales**: Identifica y programa adecuadamente clases especiales como "Semana Tec" o "Etapas de Evaluación".

### English

- **Automatic schedule PDF parsing**: No need to manually enter your classes; the script extracts all necessary information from the PDF.
- **Generates .ics files**: Creates calendar files compatible with most calendar applications.
- **Excludes specific weeks**: Automatically omits classes during weeks designated for special activities (e.g., weeks 6, 12, and 18).
- **Supports special classes**: Identifies and appropriately schedules special classes like "Semana Tec" or "Evaluation Weeks".

---

## Requisitos / Requirements

### Español

- **Python 3.x**
- **Bibliotecas Python**:
  - PyMuPDF (fitz)
  - pytz
  - icalendar

### English

- **Python 3.x**
- **Python Libraries**:
  - PyMuPDF (fitz)
  - pytz
  - icalendar

---

## Instalación de Dependencias / Install Dependencies

### Español

Abre una terminal y ejecuta el siguiente comando para instalar las dependencias necesarias:

```bash
pip install PyMuPDF pytz icalendar
```

### English

Open a terminal and run the following command to install the necessary dependencies:

```bash
pip install PyMuPDF pytz icalendar
```

---

## Uso / Usage

### Español

1. **Coloca el PDF de tu horario** en la carpeta `Descargas` de tu usuario.

2. **Ejecuta el script**:

    ```bash
    python horarios.py
    ```

3. **Sigue las instrucciones en pantalla**:

    - Ingresa el nombre del archivo PDF (sin la extensión `.pdf`).
    - Proporciona la fecha actual y la fecha de inicio del semestre en el formato solicitado (`YYYY-MM-DD`).

4. **Importa los archivos .ics generados**:

    - Los archivos se guardarán en la carpeta `Horarios` dentro de `Descargas`.
    - Importa estos archivos en tu aplicación de calendario preferida.

### English

1. **Place your schedule PDF** in your user's `Downloads` folder.

2. **Run the script**:

    ```bash
    python horarios.py
    ```

3. **Follow the on-screen instructions**:

    - Enter the name of the PDF file (without the `.pdf` extension).
    - Provide the current date and the semester start date in the requested format (`YYYY-MM-DD`).

4. **Import the generated .ics files**:

    - The files will be saved in the `Horarios` folder within `Downloads`.
    - Import these files into your preferred calendar application.

---

## Estructura del Proyecto / Project Structure

```
.
├── horarios.py
├── README.md
```

- **horarios.py**: Script principal para generar los archivos `.ics`. | Main script to generate the `.ics`. files.
- **README.md**: Este archivo. | This file.

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
