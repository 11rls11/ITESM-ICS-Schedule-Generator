import os
import re
from datetime import datetime, timedelta

import fitz  # PyMuPDF para leer PDFs
import pytz
from icalendar import Calendar, Event, vText


def parse_pdf(file_path):
    """Analiza el PDF y extrae los datos del horario."""
    pdf_document = fitz.open(file_path)
    text = ""

    # Leer todo el texto del PDF
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        page_text = page.get_text("text")
        text += page_text
    pdf_document.close()

    # Procesar el texto extraído
    lines = text.split('\n')
    schedule_data = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detectar el inicio de una Unidad de Formación
        if line.lower().startswith('unidad de formación:'):
            subject_code = line[len('Unidad de formación:'):].strip()
            i += 1

            # Saltar líneas vacías
            while i < len(lines) and lines[i].strip() == '':
                i += 1

            # Nombre de la materia
            subject = lines[i].strip() if i < len(lines) else ''
            i += 1

            # Obtener profesores
            professor_lines = []
            while (i < len(lines) and not re.match(
                    r'^(Lun|Mar|Mié|Jue|Vie|Sáb|Dom)',
                    lines[i].strip(), re.IGNORECASE)):
                professor_lines.append(lines[i].strip())
                i += 1
            professor = ' '.join(professor_lines).strip()

            # Obtener días y horas
            days_times_line = ''
            while i < len(lines):
                line = lines[i].strip()
                if re.match(r'^(Lun|Mar|Mié|Jue|Vie|Sáb|Dom)', line, re.IGNORECASE):
                    days_times_line = line
                    i += 1
                    break
                else:
                    i += 1

            days_pattern = r'(Lun|Mar|Mié|Jue|Vie|Sáb|Dom)'
            days = re.findall(days_pattern, days_times_line, re.IGNORECASE)
            times_pattern = r'(\d{1,2}:\d{2})'
            times = re.findall(times_pattern, days_times_line)
            start_time, end_time = (times[0], times[1]) if len(times) >= 2 else ('', '')

            # Obtener fechas de inicio y fin
            dates_line = ''
            while i < len(lines):
                line = lines[i].strip()
                if re.match(r'^\d{2}\.\d{2}\.\d{4}\s*-\s*\d{2}\.\d{2}\.\d{4}', line):
                    dates_line = line
                    i += 1
                    break
                else:
                    i += 1

            if dates_line:
                start_date_str, end_date_str = dates_line.split(' - ')
                start_date = datetime.strptime(start_date_str.strip(), '%d.%m.%Y')
                end_date = datetime.strptime(end_date_str.strip(), '%d.%m.%Y')
            else:
                print(f"Fechas no reconocidas para la clase '{subject}'. Línea de fecha: '{dates_line}'")
                continue

            # Ubicación
            location_lines = []
            while (i < len(lines) and not lines[i].strip().lower().startswith('sub-período')
                   and lines[i].strip() != ''):
                location_lines.append(lines[i].strip())
                i += 1
            location = ' '.join(location_lines).strip() if location_lines else 'Sin sala'

            # Sub-período y CRN
            subperiodo = ''
            crn = ''
            if i < len(lines) and 'Sub-período' in lines[i]:
                match = re.search(r'Sub-período\s*(.*?)\s*\|\s*CRN\s*(\S+)', lines[i])
                if match:
                    subperiodo = match.group(1).strip()
                    crn = match.group(2).strip()
                i += 1

            # Formato (Presencial/Remoto)
            formato = ''
            if i < len(lines) and ('Presencial' in lines[i] or 'Remoto' in lines[i]):
                formato = lines[i].strip()
                i += 1

            # Identificar si es una clase especial
            is_special_class = False
            special_keywords = [
                'ST -', '18 -', 'Semana 18', 'Semana Tec', 'Evaluación Etapa Inicial'
            ]
            for keyword in special_keywords:
                if keyword.lower() in subject.lower():
                    is_special_class = True
                    break

            class_duration = (end_date - start_date).days + 1
            if class_duration <= 7:
                is_special_class = True

            # Depuración
            print("--- Clase detectada ---")
            print(f"Código de la materia: {subject_code}")
            print(f"Materia: {subject}")
            print(f"Profesor(es): {professor}")
            print(f"Sub-período: {subperiodo}")
            print(f"CRN: {crn}")
            print(f"Días: {days}")
            print(f"Horario: {start_time} - {end_time}")
            print(f"Fechas: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
            print(f"Formato: {formato}")
            print(f"Ubicación: {location}")
            print(f"Clase especial: {'Sí' if is_special_class else 'No'}")
            print("---------------------------\n")

            # Agregar clase al horario
            schedule_data.append({
                'subject_code': subject_code,
                'subject': subject,
                'professor': professor,
                'subperiodo': subperiodo,
                'crn': crn,
                'days': days,
                'start_time': start_time,
                'end_time': end_time,
                'start_date': start_date,
                'end_date': end_date,
                'format': formato,
                'location': location,
                'is_special_class': is_special_class
            })
        else:
            i += 1

    return schedule_data


def generate_exclude_dates(semester_start_date, weeks):
    """Genera las fechas a excluir (semana 6, 12, 18)."""
    exclude_dates = []
    for week in weeks:
        week_start = semester_start_date + timedelta(weeks=week)
        week_dates = [week_start + timedelta(days=n) for n in range(7)]
        exclude_dates.extend(week_dates)
    return [d.date() for d in exclude_dates]


def ask_colors_for_subjects(schedule_data):
    """Pregunta al usuario por un color para cada materia distinta."""
    subjects = {item['subject'] for item in schedule_data}
    subject_colors = {}

    print("Por favor, asigna un color a cada materia (e.g., 'red', 'blue', 'green').")
    for subj in subjects:
        while True:
            color = input(f"Color para '{subj}': ").strip()
            if color:
                subject_colors[subj] = color
                break
            else:
                print("El color no puede estar vacío. Intenta de nuevo.")
    return subject_colors


def create_ics_files(schedule_data, current_date, semester_start_date, subject_colors):
    """Crea los archivos ICS a partir de los datos del horario."""
    output_dir = os.path.expanduser("~/Downloads/Horarios")
    os.makedirs(output_dir, exist_ok=True)

    day_mapping = {
        "Lun": "MO",
        "Mar": "TU",
        "Mié": "WE",
        "Jue": "TH",
        "Vie": "FR",
        "Sáb": "SA",
        "Dom": "SU"
    }

    # Zona horaria
    tz = pytz.timezone('America/Mexico_City')

    # Semanas a excluir
    weeks_to_exclude = [5, 11, 17]
    exclude_dates = generate_exclude_dates(semester_start_date, weeks_to_exclude)

    for item in schedule_data:
        # Validaciones
        if item["start_date"] is None or item["end_date"] is None:
            print(f"Fechas inválidas para la clase '{item['subject']}'. Omitiendo...")
            continue
        if item["end_date"] < current_date:
            print(f"Clase '{item['subject']}' finalizada. Omitiendo...")
            continue
        if not item["start_time"] or not item["end_time"]:
            print(f"Horario no definido correctamente para la clase '{item['subject']}'. Omitiendo...")
            continue
        if not item["days"]:
            print(f"Días no definidos para la clase '{item['subject']}'. Omitiendo...")
            continue

        cal = Calendar()
        cal.add('prodid', '-//Mi Horario//mx')
        cal.add('version', '2.0')
        cal.add('X-WR-TIMEZONE', tz.zone)

        # Horarios de inicio y fin
        try:
            start_time_obj = datetime.strptime(item["start_time"], "%H:%M").time()
            end_time_obj = datetime.strptime(item["end_time"], "%H:%M").time()
        except ValueError:
            print(f"Formato de hora incorrecto en la clase '{item['subject']}'. Omitiendo...")
            continue

        # Fecha de la primera ocurrencia
        first_day_date = None
        for day in item["days"]:
            day_name = day.capitalize()
            day_index = (list(day_mapping.keys()).index(day_name) - item["start_date"].weekday()) % 7
            potential_date = item["start_date"] + timedelta(days=day_index)
            if potential_date >= current_date:
                first_day_date = potential_date
                break
        if not first_day_date:
            first_day_date = item["start_date"]

        event = Event()
        event.add('summary', item["subject"])

        event.add('dtstart', tz.localize(datetime.combine(first_day_date, start_time_obj)))
        event.add('dtend', tz.localize(datetime.combine(first_day_date, end_time_obj)))

        # Recurrencia
        days_of_week = [day_mapping[day.capitalize()] for day in item["days"]]
        until_date = tz.localize(datetime.combine(item["end_date"] + timedelta(days=1), datetime.min.time()))
        rrule = {
            'freq': 'weekly',
            'byday': days_of_week,
            'until': until_date
        }
        event.add('rrule', rrule)

        # Excepciones si no es clase especial
        if not item['is_special_class']:
            exdates = []
            for exclude_date in exclude_dates:
                for day in item["days"]:
                    day_name = day.capitalize()
                    if exclude_date.weekday() == list(day_mapping.keys()).index(day_name):
                        exdate = tz.localize(datetime.combine(exclude_date, start_time_obj))
                        exdates.append(exdate)
            if exdates:
                event.add('exdate', exdates)
                print(f"Fechas de exclusión para '{item['subject']}': {[dt.strftime('%Y-%m-%d') for dt in exdates]}")
        else:
            print(f"La clase '{item['subject']}' es especial. Se programará en semanas especiales.")

        # Descripción
        description = (
            f"Profesor(es): {item['professor']}\n"
            f"Sub-período: {item['subperiodo']}\n"
            f"CRN: {item['crn']}\n"
            f"Formato: {item['format']}\n"
            f"Ubicación: {item['location']}\n"
            f"Días: {', '.join(item['days'])}\n"
            f"Horario: {item['start_time']} - {item['end_time']}\n"
            f"Periodo: {item['start_date'].strftime('%d/%m/%Y')} - {item['end_date'].strftime('%d/%m/%Y')}"
        )
        event.add('location', vText(item["location"]))
        event.add('description', vText(description))

        # Añadir el color como categoría
        color = subject_colors.get(item['subject'], 'Sin color')
        event.add('categories', vText(color))

        cal.add_component(event)

        # Guardar el archivo ICS
        safe_subject = re.sub(r'\s+', '_', item['subject'])
        file_name = os.path.join(output_dir, f"{safe_subject}.ics")
        with open(file_name, 'wb') as f:
            f.write(cal.to_ical())
        print(f"Archivo ICS guardado en {file_name}")

    print("Proceso completado.")


def get_valid_file_path():
    """Solicita al usuario un nombre de archivo válido hasta que se proporcione uno existente."""
    while True:
        file_name = input("Ingresa el nombre del archivo PDF (sin extensión): ").strip()
        file_path = os.path.expanduser(f"~/Downloads/{file_name}.pdf")
        if os.path.isfile(file_path):
            return file_path
        else:
            print(f"El archivo '{file_path}' no existe. Verifica el nombre y la ubicación.")


def get_valid_date(prompt):
    """Solicita al usuario una fecha válida en formato YYYY-MM-DD."""
    while True:
        date_str = input(prompt).strip()
        try:
            valid_date = datetime.strptime(date_str, "%Y-%m-%d")
            return valid_date
        except ValueError:
            print("Formato de fecha incorrecto. Usa el formato YYYY-MM-DD.")


def main():
    """Función principal."""
    file_path = get_valid_file_path()
    current_date = get_valid_date("Ingresa la fecha actual (YYYY-MM-DD): ")
    semester_start_date = get_valid_date("Ingresa la fecha de inicio del semestre (YYYY-MM-DD): ")

    schedule_data = parse_pdf(file_path)
    subject_colors = ask_colors_for_subjects(schedule_data)
    create_ics_files(schedule_data, current_date, semester_start_date, subject_colors)


if __name__ == "__main__":
    main()
