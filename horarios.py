import os
import re
from datetime import datetime, timedelta, date

import fitz
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

            # Obtener información de la clase
            class_info, i = parse_class_info(lines, i)

            # Identificar si es una clase especial
            is_special_class = False
            special_keywords = [
                'ST -', '18 -', 'Semana 18', 'Semana Tec', 'Evaluación Etapa Inicial'
            ]
            for keyword in special_keywords:
                if keyword.lower() in subject.lower():
                    is_special_class = True
                    break

            class_duration = (class_info['end_date'] - class_info['start_date']).days + 1
            if class_duration <= 7:
                is_special_class = True

            # Depuración
            print("--- Clase detectada ---")
            print(f"Código de la materia: {subject_code}")
            print(f"Materia: {subject}")
            print(f"Profesor(es): {professor}")
            print(f"Sub-período: {class_info['subperiodo']}")
            print(f"CRN: {class_info['crn']}")
            print(f"Días: {class_info['days']}")
            print(f"Horario: {class_info['start_time']} - {class_info['end_time']}")
            print(f"Fechas: {class_info['start_date'].strftime('%d/%m/%Y')} - {class_info['end_date'].strftime('%d/%m/%Y')}")
            print(f"Formato: {class_info['format']}")
            print(f"Ubicación: {class_info['location']}")
            print(f"Clase especial: {'Sí' if is_special_class else 'No'}")
            print("---------------------------\n")

            # Agregar clase al horario
            schedule_data.append({
                'subject_code': subject_code,
                'subject': subject,
                'professor': professor,
                'subperiodo': class_info['subperiodo'],
                'crn': class_info['crn'],
                'days': class_info['days'],
                'start_time': class_info['start_time'],
                'end_time': class_info['end_time'],
                'start_date': class_info['start_date'],
                'end_date': class_info['end_date'],
                'format': class_info['format'],
                'location': class_info['location'],
                'is_special_class': is_special_class
            })
        else:
            i += 1

    return schedule_data

def parse_class_info(lines, i):
    class_info = {
        'days': [], 'start_time': '', 'end_time': '', 'start_date': None, 'end_date': None,
        'location': '', 'subperiodo': '', 'crn': '', 'format': ''
    }
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Días y horarios
        if re.match(r'^(Lun|Mar|Mié|Jue|Vie|Sáb|Dom)', line, re.IGNORECASE):
            days_pattern = r'(Lun|Mar|Mié|Jue|Vie|Sáb|Dom)'
            class_info['days'] = re.findall(days_pattern, line, re.IGNORECASE)
            times = re.findall(r'(\d{1,2}:\d{2})', line)
            if len(times) >= 2:
                class_info['start_time'], class_info['end_time'] = times[0], times[1]
        
        # Fechas
        elif re.match(r'^\d{2}\.\d{2}\.\d{4}\s*-\s*\d{2}\.\d{2}\.\d{4}', line):
            start_date_str, end_date_str = line.split(' - ')
            class_info['start_date'] = datetime.strptime(start_date_str.strip(), '%d.%m.%Y')
            class_info['end_date'] = datetime.strptime(end_date_str.strip(), '%d.%m.%Y')
        
        # Ubicación
        elif 'GDA' in line or 'Edificio' in line:
            class_info['location'] += line + ' '
        
        # Sub-período y CRN
        elif 'Sub-período' in line:
            match = re.search(r'Sub-período\s*(.*?)\s*\|\s*CRN\s*(\S+)', line)
            if match:
                class_info['subperiodo'] = match.group(1).strip()
                class_info['crn'] = match.group(2).strip()
        
        # Formato
        elif 'Presencial' in line or 'Remoto' in line:
            class_info['format'] = line
        
        # Salir del bucle si hemos procesado toda la información relevante
        elif class_info['days'] and class_info['start_date'] and class_info['end_date'] and class_info['location']:
            break
        
        i += 1
    
    return class_info, i

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
    color_options = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'cyan', 'magenta', 'lime', 'teal', 'lavender', 'brown', 'beige', 'maroon', 'mint', 'olive', 'apricot', 'navy', 'grey']
    
    print("Opciones de colores disponibles:", ", ".join(color_options))
    print("Por favor asigna un color para cada materia de las opciones que tienes arriba.")
    
    for subj in subjects:
        while True:
            color = input(f"Color para '{subj}': ").strip().lower()
            if color in color_options:
                subject_colors[subj] = color
                break
            else:
                print(f"Color inválido. Por favor, elige entre: {', '.join(color_options)}")
    
    return subject_colors


def create_ics_files(schedule_data, current_date, semester_start_date, subject_colors):
    """Crea los archivos ICS a partir de los datos del horario."""
    try:
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

        # Define períodos académicos
        period1_start = semester_start_date.date()
        period1_end = period1_start + timedelta(weeks=5) - timedelta(days=1)  # Feb 10 - Mar 16
        
        period2_start = period1_end + timedelta(days=8)  # Mar 24 (después del descanso)
        period2_end = period2_start + timedelta(weeks=6) - timedelta(days=1)  # Mar 24 - May 4
        
        period3_start = period2_end + timedelta(days=8)  # May 12 (después del descanso)
        period3_end = period3_start + timedelta(weeks=5) - timedelta(days=1)  # May 12 - Jun 15

        periods = [
            {'start': period1_start, 'end': period1_end},
            {'start': period2_start, 'end': period2_end},
            {'start': period3_start, 'end': period3_end}
        ]

        # Días festivos fijos
        fixed_holidays = [
            datetime(2025, 3, 17).date(),  # Asueto
            datetime(2025, 5, 1).date(),   # Día del Trabajo
        ]

        # Semana Santa
        holy_week_start = datetime(2025, 4, 14).date()
        holy_week_end = datetime(2025, 4, 20).date()

        for item in schedule_data:
            try:
                if item["end_date"] < current_date:
                    print(f"La clase '{item['subject']}' ya finalizó. Omitiendo...")
                    continue

                if item['is_special_class']:
                    cal = Calendar()
                    cal.add('prodid', '-//Mi Horario//mx')
                    cal.add('version', '2.0')
                    cal.add('X-WR-TIMEZONE', tz.zone)

                    # Calcular exclusiones para clases especiales
                    exclusions = []
                    class_start = item["start_date"].date()
                    class_end = item["end_date"].date()
    
                    # Agregar días festivos
                    exclusions.extend([d for d in fixed_holidays 
                                      if class_start <= d <= class_end])

                    # Obtener días de clase
                    class_days = [list(day_mapping.keys()).index(day.capitalize()) 
                                 for day in item["days"]]

                    # Filtrar exclusiones por días de clase
                    current_excludes = [
                        date for date in exclusions
                        if date.weekday() in class_days
                    ]

                    # Crear evento para clase especial
                    event = Event()
                    event.add('summary', item["subject"])

                    # Configurar horarios
                    start_time = datetime.strptime(item["start_time"], "%H:%M").time()
                    end_time = datetime.strptime(item["end_time"], "%H:%M").time()

                    # Calcular primer día
                    class_days = [list(day_mapping.keys()).index(day.capitalize()) 
                                for day in item["days"]]
                    first_day = next(
                        (item["start_date"].date() + timedelta(days=((d - item["start_date"].date().weekday()) % 7))
                         for d in class_days
                         if (item["start_date"].date() + timedelta(days=((d - item["start_date"].date().weekday()) % 7))) >= item["start_date"].date()),
                        item["start_date"].date()
                    )

                    event.add('dtstart', tz.localize(datetime.combine(first_day, start_time)))
                    event.add('dtend', tz.localize(datetime.combine(first_day, end_time)))

                    # Configurar recurrencia si dura más de un día
                    if (item["end_date"].date() - item["start_date"].date()).days > 0:
                        days_of_week = [day_mapping[day.capitalize()] for day in item["days"]]
                        until_date = tz.localize(datetime.combine(item["end_date"].date() + timedelta(days=1), 
                                                                datetime.min.time()))
                        event.add('rrule', {
                            'freq': 'weekly',
                            'byday': days_of_week,
                            'until': until_date
                        })

                    # Añadir exclusiones
                    if current_excludes:
                        exdates = [tz.localize(datetime.combine(d, start_time))
                                    for d in current_excludes]
                        event.add('exdate', exdates)
                        print(f"Fechas de exclusión para '{item['subject']}': {[dt.strftime('%d/%m/%Y') for dt in exdates]}")


                    # Agregar metadatos
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
                    event.add('categories', vText(subject_colors.get(item['subject'], 'grey')))
                    event.add('color', subject_colors.get(item['subject'], 'grey'))

                    cal.add_component(event)

                    # Guardar archivo ICS
                    safe_subject = re.sub(r'\s+', '_', item['subject'])
                    file_name = os.path.join(output_dir, f"{safe_subject}.ics")
                    
                    with open(file_name, 'wb') as f:
                        f.write(cal.to_ical())
                    print(f"Archivo ICS guardado en {file_name}")
                    continue

                for period in periods:
                    # Verificar si la clase cae en este período
                    class_start = max(item["start_date"].date(), period['start'])
                    class_end = min(item["end_date"].date(), period['end'])
                    
                    if class_start > class_end:
                        continue

                    cal = Calendar()
                    cal.add('prodid', '-//Mi Horario//mx')
                    cal.add('version', '2.0')
                    cal.add('X-WR-TIMEZONE', tz.zone)

                    # Calcular exclusiones para este período
                    exclusions = []
                    
                    # Agregar días festivos
                    exclusions.extend([d for d in fixed_holidays 
                                     if class_start <= d <= class_end])
                    
                    # Agregar Semana Santa si está dentro del período
                    current = holy_week_start
                    while current <= holy_week_end:
                        if class_start <= current <= class_end:
                            exclusions.append(current)
                        current += timedelta(days=1)

                    # Obtener días de clase
                    try:
                        class_days = [list(day_mapping.keys()).index(day.capitalize()) 
                                    for day in item["days"]]
                    except (KeyError, ValueError) as e:
                        print(f"Error al procesar los días para la clase '{item['subject']}': {str(e)}")
                        continue

                    # Filtrar exclusiones por días de clase
                    current_excludes = [
                        date for date in exclusions
                        if date.weekday() in class_days
                    ]

                    # Crear evento
                    event = Event()
                    event.add('summary', item["subject"])

                    # Configurar horarios
                    try:
                        start_time = datetime.strptime(item["start_time"], "%H:%M").time()
                        end_time = datetime.strptime(item["end_time"], "%H:%M").time()
                    except ValueError as e:
                        print(f"Error en formato de hora para la clase '{item['subject']}': {str(e)}")
                        continue

                    # Calcular primer día de clase
                    try:
                        first_day = next(
                            (class_start + timedelta(days=((d - class_start.weekday()) % 7))
                             for d in class_days
                             if (class_start + timedelta(days=((d - class_start.weekday()) % 7))) >= class_start),
                            class_start
                        )
                    except Exception as e:
                        print(f"Error al calcular el primer día para la clase '{item['subject']}': {str(e)}")
                        continue

                    event.add('dtstart', tz.localize(datetime.combine(first_day, start_time)))
                    event.add('dtend', tz.localize(datetime.combine(first_day, end_time)))

                    # Configurar recurrencia
                    days_of_week = [day_mapping[day.capitalize()] for day in item["days"]]
                    until_date = tz.localize(datetime.combine(class_end + timedelta(days=1), 
                                                            datetime.min.time()))
                    
                    event.add('rrule', {
                        'freq': 'weekly',
                        'byday': days_of_week,
                        'until': until_date
                    })

                    # Agregar exclusiones
                    if current_excludes:
                        exdates = [tz.localize(datetime.combine(d, start_time))
                                  for d in current_excludes]
                        event.add('exdate', exdates)
                        print(f"Fechas de exclusión para '{item['subject']}': {[dt.strftime('%d/%m/%Y') for dt in exdates]}")

                    # Agregar metadatos
                    description = (
                        f"Profesor(es): {item['professor']}\n"
                        f"Sub-período: {item['subperiodo']}\n"
                        f"CRN: {item['crn']}\n"
                        f"Formato: {item['format']}\n"
                        f"Ubicación: {item['location']}\n"
                        f"Días: {', '.join(item['days'])}\n"
                        f"Horario: {item['start_time']} - {item['end_time']}\n"
                        f"Periodo: {class_start.strftime('%d/%m/%Y')} - {class_end.strftime('%d/%m/%Y')}"
                    )
                    
                    event.add('location', vText(item["location"]))
                    event.add('description', vText(description))
                    event.add('categories', vText(subject_colors.get(item['subject'], 'grey')))
                    event.add('color', subject_colors.get(item['subject'], 'grey'))

                    cal.add_component(event)

                    # Guardar archivo ICS
                    period_suffix = f"_P{periods.index(period) + 1}"
                    safe_subject = re.sub(r'\s+', '_', item['subject'])
                    file_name = os.path.join(output_dir, f"{safe_subject}{period_suffix}.ics")
                    
                    try:
                        with open(file_name, 'wb') as f:
                            f.write(cal.to_ical())
                        print(f"Archivo ICS guardado en {file_name}")
                    except IOError as e:
                        print(f"Error al guardar el archivo ICS para la clase '{item['subject']}': {str(e)}")

            except Exception as e:
                print(f"Error al procesar la clase '{item['subject']}': {str(e)}")
                continue

        print("Proceso completado exitosamente.")
    except Exception as e:
        print(f"Error general en la creación de archivos ICS: {str(e)}")



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
