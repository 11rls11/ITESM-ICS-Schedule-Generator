import os
import re
from datetime import datetime, timedelta

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

'''
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
'''

# def create_ics_files(schedule_data, current_date, semester_start_date, subject_colors):
def create_ics_files(schedule_data, current_date, semester_start_date):
    """Crea los archivos ICS"""
    try:
        # Configuración inicial
        output_dir = os.path.expanduser("~/Downloads/Horarios")
        os.makedirs(output_dir, exist_ok=True)
        tz = pytz.timezone('America/Mexico_City')

        def create_calendar():
            cal = Calendar()
            cal.add('prodid', '-//Mi Horario//mx')
            cal.add('version', '2.0')
            cal.add('X-WR-TIMEZONE', tz.zone)
            return cal

        def setup_event(event, item, class_start, class_end):
            """Configuración común para todos los eventos."""
            start_time = datetime.strptime(item["start_time"], "%H:%M").time()
            end_time = datetime.strptime(item["end_time"], "%H:%M").time()
            
            event.add('summary', item["subject"])
            event.add('location', vText(item["location"]))
            event.add('dtstart', tz.localize(datetime.combine(class_start, start_time)))
            event.add('dtend', tz.localize(datetime.combine(class_start, end_time)))
            
            description = (
                f"Profesor(es): {item['professor']}\n"
                f"Sub-período: {item['subperiodo']}\n"
                f"CRN: {item['crn']}\n"
                f"Formato: {item['format']}\n"
                f"Días: {', '.join(item['days'])}\n"
                f"Horario: {item['start_time']} - {item['end_time']}"
            )
            event.add('description', vText(description))
            # event.add('categories', vText(subject_colors.get(item['subject'], 'grey')))
            # event.add('color', subject_colors.get(item['subject'], 'grey'))
            
            return start_time, end_time

        def handle_recurrence(event, class_start, class_end, days_of_week):
            """Maneja la configuración de recurrencia."""
            if (class_end - class_start).days > 0:
                event.add('rrule', {
                    'freq': 'weekly',
                    'byday': [day_mapping[day.capitalize()] for day in days_of_week],
                    'until': tz.localize(datetime.combine(
                        class_end + timedelta(days=1), 
                        datetime.min.time()
                    ))
                })

        def calculate_exclusions(start_date, end_date):
            """Calcula fechas de exclusión comunes."""
            exclusions = [
                d for d in fixed_holidays
                if start_date <= d <= end_date
            ]
            
            # Semana Santa
            current = holy_week_start
            while current <= holy_week_end:
                if start_date <= current <= end_date:
                    exclusions.append(current)
                current += timedelta(days=1)
            
            return exclusions

        # Configuración de días
        day_mapping = {"Lun": "MO", "Mar": "TU", "Mié": "WE", 
                      "Jue": "TH", "Vie": "FR", "Sáb": "SA", "Dom": "SU"}
        
        # Definición de períodos académicos
        period1_start = semester_start_date.date()
        period1_end = period1_start + timedelta(weeks=5) - timedelta(days=1)

        period2_start = period1_end + timedelta(days=8)
        period2_end = period2_start + timedelta(weeks=6) - timedelta(days=1)

        period3_start = period2_end + timedelta(days=8)  # May 5
        period3_end = period3_start + timedelta(weeks=5) - timedelta(days=1)

        period_defs = [
            {'start': period1_start, 'end': period1_end},
            {'start': period2_start, 'end': period2_end},
            {'start': period3_start, 'end': period3_end}
        ]

        # Configuración de días festivos
        fixed_holidays = [datetime(2024, 9, 16).date(), datetime(2024, 10, 1).date(), datetime(2024, 11, 18).date(), datetime(2025, 3, 17).date(), datetime(2025, 5, 1).date(), datetime(2025, 9, 16).date(), datetime(2025, 11, 17).date()]
        holy_week_start = datetime(2025, 4, 14).date()
        holy_week_end = datetime(2025, 4, 20).date()

        # Procesamiento principal
        for item in schedule_data:
            if item["end_date"].date() < current_date.date():
                print(f"Clase omitida: {item['subject']} (finalizada)")
                continue

            try:
                if item['is_special_class']:
                    cal = create_calendar()
                    event = Event()
                    
                    start_time, end_time = setup_event(
                        event, 
                        item,
                        item["start_date"].date(),
                        item["end_date"].date()
                    )
                    
                    # Manejo de exclusiones
                    exclusions = calculate_exclusions(
                        item["start_date"].date(), 
                        item["end_date"].date()
                    )
                    
                    if exclusions:
                        event.add('exdate', [
                            tz.localize(datetime.combine(d, start_time))
                            for d in exclusions
                        ])
                        print(f"Exclusiones: {item['subject']} - {len(exclusions)} días")

                    handle_recurrence(event, 
                                    item["start_date"].date(),
                                    item["end_date"].date(),
                                    item["days"])
                    
                    cal.add_component(event)
                    save_ics_file(cal, item)

                else:
                    for idx, period in enumerate(period_defs, 1):
                        class_start = max(item["start_date"].date(), period['start'])
                        class_end = min(item["end_date"].date(), period['end'])
                        
                        if class_start > class_end:
                            continue

                        cal = create_calendar()
                        event = Event()
                        
                        start_time, _ = setup_event(
                            event, 
                            item,
                            class_start,
                            class_end
                        )
                        
                        exclusions = calculate_exclusions(class_start, class_end)
                        
                        if exclusions:
                            event.add('exdate', [
                                tz.localize(datetime.combine(d, start_time))
                                for d in exclusions
                            ])
                            print(f"Exclusiones: {item['subject']} P{idx} - {len(exclusions)} días")

                        handle_recurrence(event, class_start, class_end, item["days"])
                        
                        cal.add_component(event)
                        save_ics_file(cal, item, f"_P{idx}")

            except Exception as e:
                print(f"Error procesando {item['subject']}: {str(e)}")

        print("Proceso completado correctamente.")
    
    except Exception as e:
        print(f"Error crítico: {str(e)}")

def save_ics_file(cal, item, suffix=''):
    """Guarda el archivo ICS con formato consistente."""
    output_dir = os.path.expanduser("~/Downloads/Horarios")
    safe_name = re.sub(r'\s+', '_', item['subject']).strip('_')
    filename = os.path.join(output_dir, f"{safe_name}{suffix}.ics")
    
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())
    print(f"Archivo guardado: {filename}")


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
    # subject_colors = ask_colors_for_subjects(schedule_data)
    # create_ics_files(schedule_data, current_date, semester_start_date, subject_colors)
    create_ics_files(schedule_data, current_date, semester_start_date)

if __name__ == "__main__":
    main()
