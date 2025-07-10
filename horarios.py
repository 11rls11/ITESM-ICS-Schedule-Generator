# horarios.py
# Tecnológico de Monterrey's Schedule Parser from .pdf to .ics
# Made by 11rls11
# Fecha de última modificación: 09/07/2025

import os
import re
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple, Any

import fitz
import pytz
from icalendar import Calendar, Event, vText

# ================================= #
# CONSTANTES Y CONFIGURACIÓN GLOBAL #
# ================================= #

DEFAULT_FORMAT = 'Presencial'
TIMEZONE = 'America/Mexico_City'
FIXED_HOLIDAYS = [
    (5, 1),   # Día del Trabajo
    (9, 16),  # Independencia de México
]
MONDAY_HOLIDAYS = {
    'constitucion': (2, 1),  # Día de la constitución mexicana
    'natalicio': (3, 3),    # Natalicio de Benito Juarez
    'revolucion': (11, 3) # Revolución Mexicana
}
SPECIAL_CLASS_KEYWORDS = ['st -', '18 -', 'semana 18', 'semana tec']

DAY_MAPPING = {
    "Lun": "MO", "Mar": "TU", "Mié": "WE", 
    "Jue": "TH", "Vie": "FR", "Sáb": "SA", "Dom": "SU"
}
DAYS_MAPPING = {
    'Lun': 0, 'Mar': 1, 'Mié': 2, 'Jue': 3, 'Vie': 4, 'Sáb': 5, 'Dom': 6
}

# ================================== #
# FUNCIONES PRINCIPALES DEL PROGRAMA #
# ================================== #

def main() -> None:
    """Función principal del programa."""
    file_path = get_valid_file_path()
    current_date = get_valid_date("Ingresa la fecha actual (DD-MM-YYYY): ")
    semester_start_date = get_valid_date("Ingresa la fecha de inicio del semestre (DD-MM-YYYY): ")

    parsing = parse_pdf(file_path)
    create_ics_file(parsing, current_date, semester_start_date)

def get_valid_file_path() -> str:
    """
    Solicita al usuario un nombre de archivo PDF válido.
    
    Returns:
        Ruta al archivo PDF
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    while True:
        file_name = input("Ingresa el nombre del archivo PDF (sin extensión): ").strip()
        file_path = os.path.join(current_dir, f"{file_name}.pdf")
        
        if os.path.isfile(file_path):
            return file_path
            
        print(f"El archivo '{file_name}.pdf' no existe en el directorio actual. Verifica el nombre.")

def get_valid_date(prompt: str) -> datetime:
    """
    Solicita al usuario una fecha válida en formato DD-MM-YYYY.
    
    Args:
        prompt: Mensaje del usuario
        
    Returns:
        Fecha válida ingresada por el usuario
    """
    while True:
        date_str = input(prompt).strip()
        try:
            valid_date = datetime.strptime(date_str, "%d-%m-%Y")
            return valid_date
        except ValueError:
            print("Formato de fecha incorrecto. Usa el formato DD-MM-YYYY.")

# =============================================== # 
# FUNCIONES DE PROCESAMIENTO DEL PDF DEL HORARIOS #
# =============================================== #

def parse_pdf(file_path: str) -> Dict[str, Any]:
    """
    Analiza el PDF y extrae los datos del horario.
    
    Args:
        file_path: Ruta al archivo PDF
        
    Returns:
        Diccionario con la información extraída del PDF
    """
    try:
        pdf_document = fitz.open(file_path)
        text = ""
        for page in pdf_document:
            text += page.get_text("text")
        pdf_document.close()
        
        lines = text.split('\n')
        
        process_date, campus, career = extract_header_info(lines)
        
        subject_indexes = find_subject_indexes(lines)
        
        schedule_data = []
        for idx, start_idx in enumerate(subject_indexes):
            # Determinar el final del bloque
            end_idx = subject_indexes[idx + 1] if idx + 1 < len(subject_indexes) else len(lines)
            block_lines = lines[start_idx:end_idx]
            
            try:
                class_infos = extract_subject_info(block_lines)
                
                if not class_infos:
                    print(f"No se pudo extraer información de la materia en el bloque {idx+1}")
                    continue
                
                for subject_info in class_infos:
                    if not is_valid_subject_info(subject_info):
                        print("Saltando horario de materia por falta de datos")
                        continue
                        
                    # Determinar si es Semana TEC
                    class_duration = (subject_info['end_date'] - subject_info['start_date']).days + 1
                    is_special_class = is_special_class_check(class_duration, subject_info['subject'])
                    subject_info['is_special_class'] = is_special_class
                    
                    subject_info['campus'] = campus
                    subject_info['career'] = career
                    subject_info['process_date'] = process_date
                    
                    print_class_info(subject_info, is_special_class)
                    
                    schedule_data.append(subject_info)
                    
            except Exception as e:
                print(f"Error procesando bloque de materia: {str(e)}")
        
        return {
            'schedule_data': schedule_data,
            'process_date': process_date,
            'campus': campus,
            'career': career
        }
        
    except Exception as e:
        print(f"Error procesando PDF: {str(e)}")
        return {'schedule_data': [], 'process_date': '', 'campus': '', 'career': ''}

def extract_header_info(lines: List[str]) -> Tuple[str, str, str]:
    """
    Extrae información de encabezado del PDF.
    
    Args:
        lines: Lista de líneas del PDF
        
    Returns:
        Tupla con (fecha_proceso, campus, carrera)
    """
    process_date = ""
    campus = ""
    career = ""
    
    for line in lines:
        if "Última hora del comprobante:" in line:
            comprobante_match = re.search(r'Última hora del comprobante:\s*(\d{2}\.\d{2}\.\d{4})', line)
            if comprobante_match:
                process_date = comprobante_match.group(1).replace('.', '')
        
        campus_career_match = re.search(r'([A-Z]{3})\s*/\s*([^/]+)\s*/\s*([^/\n]+)', line)
        if campus_career_match:
            campus = campus_career_match.group(1).strip()
            career = campus_career_match.group(3).strip()
    
    return process_date, campus, career

def find_subject_indexes(lines: List[str]) -> List[int]:
    """
    Encuentra los índices donde comienzan las unidades de formación.
    
    Args:
        lines: Lista de líneas del PDF
        
    Returns:
        Lista de índices donde comienzan las materias
    """
    return [i for i, line in enumerate(lines) 
            if line.strip().startswith('Unidad de formación:')]

def is_valid_subject_info(subject_info: Dict[str, Any]) -> bool:
    """Verifica si la información de la materia contiene los datos mínimos necesarios."""
    return (subject_info and 
            subject_info.get('start_date') and 
            subject_info.get('end_date'))

def is_special_class_check(class_duration: int, subject: str) -> bool:
    """
    Determina si una clase es especial basada en su duración y nombre.
    
    Args:
        class_duration: Duración de la clase en días
        subject: Nombre de la materia
        
    Returns:
        True si es una clase especial, False en caso contrario
    """
    # Una clase es especial si dura una semana o menos, o si contiene palabras clave
    if class_duration <= 7:
        return True
        
    for keyword in SPECIAL_CLASS_KEYWORDS:
        if keyword in subject.lower():
            return True
            
    return False

def print_class_info(subject_info: Dict[str, Any], is_special_class: bool) -> None:
    """
    Imprime información de depuración sobre una clase.
    
    Args:
        subject_info: Información de la materia
        is_special_class: Indica si es una clase especial
    """
    print(f"\n--- Clase detectada: {subject_info['subject']} ({subject_info['subject_code']}) ---")
    print(f"Profesor(es): {subject_info.get('professor', 'No especificado')}")
    print(f"Días: {', '.join(subject_info.get('days', []))}")
    print(f"Horario: {subject_info.get('start_time')} - {subject_info.get('end_time')}")
    print(f"Fechas: {subject_info['start_date'].strftime('%d/%m/%Y')} - {subject_info['end_date'].strftime('%d/%m/%Y')}")
    print(f"Ubicación: {subject_info.get('location', 'No especificada')}")
    print(f"Clase especial: {'Sí' if is_special_class else 'No'}")

    if subject_info.get('in_english', False):
        print(f"Idioma: Inglés")

# ================================================== #
# FUNCIONES DE EXTRACCIÓN DE INFORMACIÓN DE MATERIAS #
# ================================================== #

def extract_subject_info(block_lines: List[str]) -> List[Dict[str, Any]]:
    """
    Extrae la información de una materia a partir de un bloque de líneas.
    
    Args:
        block_lines: Líneas del bloque de la materia
        
    Returns:
        Lista de diccionarios con información de los horarios de la materia
    """
    class_infos = []
    
    base_info = create_base_info_dict()
    
    code_line = block_lines[0].strip()
    base_info['subject_code'] = code_line[len('Unidad de formación:'):].strip()
    
    subject_line_idx = get_subject_line_idx(block_lines)
    if subject_line_idx < len(block_lines):
        base_info['subject'] = block_lines[subject_line_idx].strip()
    
    base_info['professor'] = extract_professor(block_lines, subject_line_idx)
    
    extract_subperiod_and_crn(block_lines, base_info)
    
    extract_location_and_format(block_lines, base_info)
    
    schedule_indexes = find_schedule_indexes(block_lines)
    
    if not schedule_indexes:
        return None
    
    extract_dates(block_lines, schedule_indexes, base_info)
    
    for schedule_idx in schedule_indexes:
        subject_info = process_schedule(block_lines, schedule_idx, base_info)
        if subject_info:
            class_infos.append(subject_info)
    
    return class_infos

def create_base_info_dict() -> Dict[str, Any]:
    """Crea un diccionario base con la estructura para información de materias."""
    return {
        'days': [], 
        'start_time': None, 
        'end_time': None, 
        'start_date': None, 
        'end_date': None,
        'location': '', 
        'format': DEFAULT_FORMAT, 
        'sub_period': '', 
        'crn': '', 
        'professor': '',
        'in_english': False
    }

def get_subject_line_idx(block_lines: List[str]) -> int:
    """
    Obtiene el índice de la línea que contiene el nombre de la materia.
    
    Args:
        block_lines: Líneas del bloque de la materia
        
    Returns:
        Índice de la línea con el nombre de la materia
    """
    subject_line_idx = 1
    while subject_line_idx < len(block_lines) and not block_lines[subject_line_idx].strip():
        subject_line_idx += 1
    return subject_line_idx

def extract_professor(block_lines: List[str], subject_line_idx: int) -> str:
    """
    Extrae el nombre del profesor del bloque de líneas.
    
    Args:
        block_lines: Líneas del bloque de la materia
        subject_line_idx: Índice de la línea con el nombre de la materia
        
    Returns:
        Nombre del profesor
    """
    professor_lines = []
    i = subject_line_idx + 1
    
    while i < len(block_lines):
        line = block_lines[i].strip()
        
        if re.match(r'^(Lun|Mar|Mié|Jue|Vie|Sáb|Dom)', line, re.IGNORECASE):
            break
            
        if line:
            professor_lines.append(line)
            
        i += 1
    
    return ' '.join(professor_lines).strip()

def extract_subperiod_and_crn(block_lines: List[str], base_info: Dict[str, Any]) -> None:
    """
    Extrae información del sub-período y CRN.
    
    Args:
        block_lines: Líneas del bloque de la materia
        base_info: Diccionario donde se almacenará la información
    """
    for line in block_lines:
        if 'Sub-período' in line or 'Sub-períodos' in line:
            base_info['sub_period'] = line
            
            sub_period_match = re.search(r'Sub-período[s]?\s+(.+?)(?=\s+CRN|$)', line)
            if sub_period_match:
                base_info['sub_period_clean'] = sub_period_match.group(1).strip()
            
            crn_match = re.search(r'CRN\s+(\d+)', line)
            if crn_match:
                base_info['crn'] = crn_match.group(1)
            
            break

def extract_location_and_format(block_lines: List[str], base_info: Dict[str, Any]) -> None:
    """
    Extrae información de ubicación y formato.
    
    Args:
        block_lines: Líneas del bloque de la materia
        base_info: Diccionario donde se almacenará la información
    """
    for line in block_lines:
        if '|' in line:
            if not ('Sub-período' in line or 'Sub-períodos' in line or 'CRN' in line):
                base_info['location'] = line.strip()
                
                if 'NAL' in line or 'Campus Nacional' in line:
                    base_info['format'] = 'Remoto nacional'
                    
                break
    
    for line in block_lines:
        if line.strip() in ['Presencial', 'Remoto nacional', 'En línea']:
            base_info['format'] = line.strip()
            break
    
    base_info['in_english'] = False
    for line in block_lines:
        if line.strip() == 'Inglés':
            base_info['in_english'] = True
            break

def find_schedule_indexes(block_lines: List[str]) -> List[int]:
    """
    Encuentra los índices de las líneas que contienen información de horarios.
    
    Args:
        block_lines: Líneas del bloque de la materia
        
    Returns:
        Lista de índices de líneas con información de horarios
    """
    indexes = []
    
    for i, line in enumerate(block_lines):
        if (re.match(r'^(Lun|Mar|Mié|Jue|Vie|Sáb|Dom)', line.strip(), re.IGNORECASE) and 
            re.search(r'\d{1,2}:\d{2}', line.strip())):
            indexes.append(i)
            
    return indexes


def extract_dates(block_lines: List[str], schedule_indexes: List[int], base_info: Dict[str, Any]) -> None:
    """
    Extrae las fechas de inicio y fin del período.
    
    Args:
        block_lines: Líneas del bloque de la materia
        schedule_indexes: Índices de las líneas con información de horarios
        base_info: Diccionario donde se almacenará la información
    """
    # Buscar fechas después de la última línea de horario
    for i in range(schedule_indexes[-1] + 1, len(block_lines)):
        line = block_lines[i].strip()
        
        # Buscar fechas en formato DD.MM.YYYY o DD/MM/YYYY
        if re.search(r'\d{2}[./]\d{2}[./]\d{4}\s*-\s*\d{2}[./]\d{2}[./]\d{4}', line):
            line = line.replace('.', '/')
            dates = re.findall(r'(\d{2}/\d{2}/\d{4})', line)
            
            if len(dates) >= 2:
                base_info['start_date'] = datetime.strptime(dates[0], '%d/%m/%Y')
                base_info['end_date'] = datetime.strptime(dates[1], '%d/%m/%Y')
                
            break

def process_schedule(block_lines: List[str], schedule_idx: int, base_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa una línea de horario y crea un objeto de información de clase.
    
    Args:
        block_lines: Líneas del bloque de la materia
        schedule_idx: Índice de la línea con información de horario
        base_info: Información base de la materia
        
    Returns:
        Diccionario con información del horario
    """
    subject_info = base_info.copy()
    
    line = block_lines[schedule_idx].strip()
    
    days_pattern = r'(Lun|Mar|Mié|Jue|Vie|Sáb|Dom)'
    subject_info['days'] = re.findall(days_pattern, line, re.IGNORECASE)
    
    times = re.findall(r'(\d{1,2}:\d{2})', line)
    if len(times) >= 2:
        subject_info['start_time'] = times[0]
        subject_info['end_time'] = times[1]
    
    if has_complete_schedule_info(subject_info):
        return subject_info
        
    return None

def has_complete_schedule_info(subject_info: Dict[str, Any]) -> bool:
    """Verifica si la información del horario está completa."""
    return (subject_info['days'] and 
            subject_info['start_time'] and 
            subject_info['end_time'] and 
            subject_info['start_date'] and 
            subject_info['end_date'])

# ======================================= #
# FUNCIONES DE CREACIÓN DE CALENDARIO ICS #
# ======================================= #

def create_ics_file(parsing: Dict[str, Any], current_date: datetime, semester_start_date: datetime) -> None:
    """
    Crea un archivo ICS para el horario completo.
    
    Args:
        parsing: Resultado del análisis del PDF
        current_date: Fecha actual
        semester_start_date: Fecha de inicio del semestre
    """
    try:
        schedule_data = parsing['schedule_data']
        process_date = parsing['process_date']
        campus = parsing['campus']
        career = parsing['career']

        tz = pytz.timezone(TIMEZONE)

        master_cal = create_master_calendar(tz)

        periods = calculate_academic_periods(semester_start_date)

        for student in schedule_data:
            student.update({
                'process_date': process_date,
                'campus': campus,
                'career': career
            })

            if student["end_date"].date() < current_date.date():
                print(f"Materia omitida: {student['subject']} (finalizada)")
                continue

            try:
                if student.get('is_special_class'):
                    process_special_class(student, master_cal, tz, current_date)
                else:
                    process_regular_class(student, periods, master_cal, tz, current_date)
            except Exception as e:
                print(f"Error procesando {student['subject']}: {str(e)}")

        save_master_ics(master_cal, process_date, campus, career)
        print("Proceso completado correctamente.")

    except Exception as e:
        print(f"Error crítico: {str(e)}")

def create_master_calendar(tz: pytz.timezone) -> Calendar:
    """Crea un calendario maestro vacío."""
    master_cal = Calendar()
    master_cal.add('prodid', '-//Mi Horario Completo//mx')
    master_cal.add('version', '2.0')
    master_cal.add('X-WR-TIMEZONE', tz.zone)
    return master_cal

def calculate_academic_periods(semester_start_date: datetime) -> List[Dict[str, date]]:
    """
    Calcula los períodos académicos basados en la fecha de inicio del semestre.
    
    Args:
        semester_start_date: Fecha de inicio del semestre
        
    Returns:
        Lista de diccionarios con fechas de inicio y fin de cada período
    """
    is_spring = semester_start_date.month == 2
    
    start_date = semester_start_date.date()
    
    if is_spring:
        # Semestre FJ (febrero-junio)
        period1_start = start_date
        period1_end = period1_start + timedelta(weeks=5) - timedelta(days=1)
        period2_start = period1_end + timedelta(days=8)
        period2_end = period2_start + timedelta(weeks=6) - timedelta(days=1)
        period3_start = period2_end + timedelta(days=8)
        period3_end = period3_start + timedelta(weeks=5) - timedelta(days=1)
    else:
        # Semestre AD (agosto-diciembre)
        period1_start = start_date
        period1_end = period1_start + timedelta(weeks=5) - timedelta(days=1)
        period2_start = period1_end + timedelta(days=8)
        period2_end = period2_start + timedelta(weeks=5) - timedelta(days=1)
        period3_start = period2_end + timedelta(days=8)
        period3_end = period3_start + timedelta(weeks=5) - timedelta(days=1)

    return [
        {'start': period1_start, 'end': period1_end},
        {'start': period2_start, 'end': period2_end},
        {'start': period3_start, 'end': period3_end}
    ]

def process_special_class(student: Dict[str, Any], master_cal: Calendar, tz: pytz.timezone, current_date: datetime) -> None:
    """
    Procesa una clase especial y la añade al calendario.
    
    Args:
        student: Información de la materia
        master_cal: Calendario maestro
        tz: Zona horaria
        current_date: Fecha actual
    """
    start_time = student["start_time"]
    end_time = student["end_time"]
    
    event = Event()
    event.add('summary', f"{student['subject']} ({student['subject_code']}) ")
    event.add('location', vText(student["location"]))
    
    start_dt = datetime.strptime(start_time, "%H:%M").time()
    end_dt = datetime.strptime(end_time, "%H:%M").time()
    
    class_start = find_first_class_day(student["start_date"].date(), student["days"])

    if class_start < current_date.date():
        class_start = find_next_class_day(current_date.date(), student["days"])

    event.add('dtstart', tz.localize(datetime.combine(class_start, start_dt)))
    event.add('dtend', tz.localize(datetime.combine(class_start, end_dt)))

    description = create_event_description(student, start_time, end_time)
    event.add('description', vText(description))

    exclusions = calculate_exclusions(class_start, student["end_date"].date())
    add_exclusions_to_event(event, exclusions, tz, student['subject'])

    if (student["end_date"].date() - class_start).days > 0:
        add_recurrence_rule(event, student["days"], student["end_date"].date(), tz)

    master_cal.add_component(event)
    print(f"Materia {student['subject']} añadida al calendario")

def process_regular_class(student: Dict[str, Any], periods: List[Dict[str, date]], master_cal: Calendar, 
                         tz: pytz.timezone, current_date: datetime) -> None:
    """
    Procesa una clase regular por períodos y la añade al calendario.
    
    Args:
        student: Información de la materia
        periods: Lista de períodos académicos
        master_cal: Calendario maestro
        tz: Zona horaria
        current_date: Fecha actual
    """
    for idx, period in enumerate(periods, 1):
        class_start = max(student["start_date"].date(), period['start'])
        class_end = min(student["end_date"].date(), period['end'])
        
        if class_end < current_date.date():
            print(f"Período {idx} de {student['subject']} omitido (finalizado)")
            continue

        if class_start <= class_end:
            start_time = student["start_time"]
            end_time = student["end_time"]
            
            event = Event()
            event.add('summary', f"{student['subject']} ({student['subject_code']})")
            event.add('location', vText(student["location"]))
            
            start_dt = datetime.strptime(start_time, "%H:%M").time()
            end_dt = datetime.strptime(end_time, "%H:%M").time()
            
            current_start = find_first_class_day(class_start, student["days"])

            if current_start < current_date.date():
                current_start = find_next_class_day(current_date.date(), student["days"])

            event.add('dtstart', tz.localize(datetime.combine(current_start, start_dt)))
            event.add('dtend', tz.localize(datetime.combine(current_start, end_dt)))

            description = create_event_description(student, start_time, end_time)
            event.add('description', vText(description))

            exclusions = calculate_exclusions(current_start, class_end)
            add_exclusions_to_event(event, exclusions, tz, f"{student['subject']} P{idx}")

            if (class_end - current_start).days > 0:
                add_recurrence_rule(event, student["days"], class_end, tz)

            master_cal.add_component(event)
            print(f"Materia {student['subject']} (Período {idx}) añadida al calendario")

def find_first_class_day(start_date: date, days: List[str]) -> date:
    """
    Encuentra el primer día de clase basado en la fecha de inicio y los días de la semana.
    
    Args:
        start_date: Fecha de inicio
        days: Lista de días de la semana
        
    Returns:
        Fecha del primer día de clase
    """
    class_days = sorted([DAYS_MAPPING[day] for day in days])
    first_day = class_days[0]
    
    current_date = start_date
    while current_date.weekday() != first_day:
        current_date += timedelta(days=1)
    
    return current_date

def find_next_class_day(current_date: date, days: List[str]) -> date:
    """
    Encuentra el próximo día de clase a partir de una fecha.
    
    Args:
        current_date: Fecha actual
        days: Lista de días de la semana
        
    Returns:
        Fecha del próximo día de clase
    """
    current_weekday = current_date.weekday()
    class_days = sorted([DAYS_MAPPING[day] for day in days])
    
    next_class_day = None
    for day in class_days:
        if day >= current_weekday:
            next_class_day = day
            break
    
    if next_class_day is not None:
        days_until_next = (next_class_day - current_weekday) % 7
    else:
        days_until_next = 7 - current_weekday + class_days[0]
    
    return current_date + timedelta(days=days_until_next)

def create_event_description(student: Dict[str, Any], start_time: str, end_time: str) -> str:
    """
    Crea la descripción para un evento del calendario.
    
    Args:
        student: Información de la materia
        start_time: Hora de inicio
        end_time: Hora de fin
        
    Returns:
        Descripción formateada para el evento
    """
    clean_professor = re.sub(r'[^\w\s,áéíóúÁÉÍÓÚñÑ]', '', student['professor'])
    sub_period_clean = student.get('sub_period_clean', '')
    crn_info = student.get('crn', '')
    in_english = student.get('in_english', False)

    description = (
        f"Profesor(es): {clean_professor}\n"
        f"Sub-período(s): {sub_period_clean}\n"
        f"CRN: {crn_info}\n"
        f"Formato: {student['format']}\n"
        f"Ubicación: {student['location']}\n"
        f"Días: {', '.join(student['days'])}\n"
        f"Horario: {start_time} - {end_time}\n"
    )

    if in_english:
        description += f"Idioma: Inglés\n"

    description += f"Período: {student['start_date'].strftime('%d/%m/%Y')} - {student['end_date'].strftime('%d/%m/%Y')}"

    return description

def calculate_easter_date(year: int) -> date:
    """
    Calcula la fecha de Pascua para un año dado usando el algoritmo de Butcher.
    
    Args:
        year: Año para calcular la Pascua
        
    Returns:
        Fecha de Pascua
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
    e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
    f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
    month = f // 31
    day = f % 31 + 1
    return date(year, month, day)

def get_holy_week_dates(year: int) -> Tuple[date, date]:
    """
    Calcula las fechas de inicio y fin de la Semana Santa para un año dado.
    
    Args:
        year: Año para calcular la Semana Santa
        
    Returns:
        Tupla con (fecha_inicio, fecha_fin) de la Semana Santa
    """
    easter_date = calculate_easter_date(year)
    # Semana Santa va del Domingo de Ramos (7 días antes) al Domingo de Pascua
    holy_week_start = easter_date - timedelta(days=7)
    holy_week_end = easter_date
    return holy_week_start, holy_week_end

def get_monday_holiday_date(year: int, month: int, week_number: int) -> date:
    """
    Calcula la fecha de un lunes de asueto.
    
    Args:
        year: Año
        month: Mes
        week_number: Número de semana (1 = primer lunes, 3 = tercer lunes)
        
    Returns:
        Fecha del día festivo móvil
    """
    # Encontrar el primer día del mes
    first_day = date(year, month, 1)
    
    days_until_monday = (7 - first_day.weekday()) % 7
    first_monday = first_day + timedelta(days=days_until_monday)
    
    # Calcular el lunes específico
    target_monday = first_monday + timedelta(weeks=week_number - 1)
    
    return target_monday

def calculate_exclusions(start_date: date, end_date: date) -> List[date]:
    """
    Calcula los días de exclusión (feriados y semana santa) para un período,
    aplicando automáticamente para todos los años en el rango.
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin
        
    Returns:
        Lista de fechas a excluir
    """
    exclusions = []
    
    start_year = start_date.year
    end_year = end_date.year
    
    for year in range(start_year, end_year + 1):
        for month, day in FIXED_HOLIDAYS:
            holiday_date = date(year, month, day)
            if start_date <= holiday_date <= end_date:
                exclusions.append(holiday_date)
        
        for holiday_name, (month, week_number) in MONDAY_HOLIDAYS.items():
            holiday_date = get_monday_holiday_date(year, month, week_number)
            if start_date <= holiday_date <= end_date:
                exclusions.append(holiday_date)
        
        holy_week_start, holy_week_end = get_holy_week_dates(year)
        
        current_day = holy_week_start
        while current_day <= holy_week_end:
            if start_date <= current_day <= end_date:
                exclusions.append(current_day)
            current_day += timedelta(days=1)
    
    exclusions = sorted(list(set(exclusions)))
    
    return exclusions

def add_exclusions_to_event(event: Event, exclusions: List[date], tz: pytz.timezone, subject_name: str) -> None:
    """
    Añade exclusiones a un evento.
    
    Args:
        event: Evento al que se añadirán las exclusiones
        exclusions: Lista de fechas a excluir
        tz: Zona horaria
        subject_name: Nombre de la materia para mensajes de depuración
    """
    if not exclusions:
        return
        
    event_start = event.get('dtstart').dt
    event.add('exdate', [
        tz.localize(datetime.combine(d, event_start.time()))
        for d in exclusions
    ])
    print(f"Exclusiones: {subject_name} - {len(exclusions)} días")


def add_recurrence_rule(event: Event, days: List[str], end_date: date, tz: pytz.timezone) -> None:
    """
    Añade una regla de recurrencia a un evento.
    
    Args:
        event: Evento al que se añadirá la regla
        days: Lista de días de la semana
        end_date: Fecha de fin
        tz: Zona horaria
    """
    event.add('rrule', {
        'freq': 'weekly',
        'byday': [DAY_MAPPING[day.capitalize()] for day in days],
        'until': tz.localize(datetime.combine(
            end_date + timedelta(days=1),
            datetime.min.time()
        ))
    })

def save_master_ics(cal: Calendar, process_date: str, campus: str, career: str) -> None:
    """
    Guarda el calendario maestro con todas las materias en un único archivo ICS.
    
    Args:
        cal: Calendario a guardar
        process_date: Fecha del proceso
        campus: Campus
        career: Carrera
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not process_date:
        process_date = datetime.now().strftime("%d%m%Y")
    if not campus:
        campus = "Campus"
    if not career:
        career = "Horario"
    
    base_filename = f"MiHorario_{process_date}_{career}"
    filename = os.path.join(current_dir, f"{base_filename}.ics")
    
    # ¿El archivo ya existe? Añadir sufijo si es necesario
    counter = 1
    while os.path.exists(filename):
        filename = os.path.join(current_dir, f"{base_filename}_{counter}.ics")
        counter += 1
    
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())
    
    print(f"Horario completo guardado en: {filename}")

if __name__ == "__main__":
    main()
