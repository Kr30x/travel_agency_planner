from flask import Flask, render_template, request, send_file, jsonify
import openpyxl
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Создаём папки если их нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


def setup_fonts():
    """Настройка русских шрифтов для ReportLab"""
    # Пробуем найти DejaVu шрифты в системе
    possible_font_paths = [
        # macOS
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        '/Library/Fonts/Arial Unicode.ttf',
        # Попробуем использовать встроенный шрифт с поддержкой Unicode
        '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
    ]
    
    # Пробуем зарегистрировать хотя бы один шрифт
    font_registered = False
    
    # Сначала пробуем Arial Unicode MS (лучший вариант для macOS)
    arial_unicode = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
    if os.path.exists(arial_unicode):
        try:
            pdfmetrics.registerFont(TTFont('RussianFont', arial_unicode))
            pdfmetrics.registerFont(TTFont('RussianFont-Bold', arial_unicode))
            print("✓ Шрифт Arial Unicode зарегистрирован")
            font_registered = True
        except Exception as e:
            print(f"⚠ Ошибка регистрации Arial Unicode: {e}")
    
    if not font_registered:
        print("⚠ Системные шрифты не найдены, используем Times-Roman (без кириллицы)")
        # Используем стандартный шрифт как fallback
        try:
            pdfmetrics.registerFont(TTFont('RussianFont', '/System/Library/Fonts/Supplemental/Times New Roman.ttf'))
            pdfmetrics.registerFont(TTFont('RussianFont-Bold', '/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf'))
            font_registered = True
            print("✓ Times New Roman зарегистрирован")
        except:
            pass
    
    return font_registered


# Инициализируем шрифты при запуске
setup_fonts()


def read_excel_file(filepath):
    """Читает Excel файл и возвращает список гостей"""
    workbook = openpyxl.load_workbook(filepath)
    sheet = workbook.active
    
    guests = []
    # Пропускаем заголовок (первая строка)
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if row[0]:  # Проверяем что строка не пустая
            guest = {
                'id': len(guests),
                'full_name': str(row[0]) if row[0] else '',
                'birth_date': str(row[1]) if row[1] else '',
                'passport': str(row[2]) if row[2] else '',
                'parent_contact': str(row[3]) if row[3] else '',
                'class': str(row[4]) if row[4] else '-',
                'status': str(row[5]) if row[5] else 'Ученик'  # Статус: Ученик или Учитель
            }
            guests.append(guest)
    
    return guests


def generate_pdf(rooms_data, output_path):
    """Генерирует PDF с распределением гостей по номерам"""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []
    
    # Создаём стили с русским шрифтом
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='RussianFont-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='RussianFont',
        fontSize=11,
        textColor=colors.HexColor('#333333')
    )
    
    # Заголовок
    title = Paragraph("Распределение гостей по номерам", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # Статистика
    total_guests = sum(len(room['guests']) for room in rooms_data)
    total_rooms = len([r for r in rooms_data if r['guests']])
    stats_text = f"Всего номеров: {total_rooms} | Всего гостей: {total_guests}"
    stats_para = Paragraph(stats_text, normal_style)
    elements.append(stats_para)
    elements.append(Spacer(1, 1*cm))
    
    # Создаём стиль для текста в ячейках
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=normal_style,
        fontSize=7.5,
        leading=9
    )
    
    # Собираем всех гостей в одну таблицу
    table_data = [['№', 'ФИО', 'Дата рожд.', 'Паспорт', 'Контакт родителя', 'Класс', 'Статус', 'Номер']]
    
    # Сортируем комнаты по номеру
    sorted_rooms = sorted(rooms_data, key=lambda r: str(r['number']))
    
    guest_counter = 1
    for room in sorted_rooms:
        if not room['guests']:  # Пропускаем пустые номера
            continue
        
        for guest in room['guests']:
            # Формируем информацию о номере
            capacity = room.get('capacity', 2)
            capacity_text = '1 м' if capacity == 1 else f'{capacity} м'
            room_info = f"{room['number']} ({capacity_text})"
            
            # Используем Paragraph для длинных текстов, чтобы они переносились
            table_data.append([
                str(guest_counter),
                Paragraph(guest['full_name'], cell_style),
                guest['birth_date'],
                guest['passport'],
                Paragraph(guest['parent_contact'], cell_style),
                guest['class'],
                guest.get('status', guest.get('role', 'Ученик')),  # Обратная совместимость
                room_info
            ])
            guest_counter += 1
    
    # Создаём таблицу
    table = Table(table_data, colWidths=[0.8*cm, 3.5*cm, 1.8*cm, 2.2*cm, 3*cm, 1*cm, 1.5*cm, 1.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Центрируем номера строк
        ('ALIGN', (-1, 0), (-1, -1), 'CENTER'),  # Центрируем номера комнат
        ('ALIGN', (5, 0), (5, -1), 'CENTER'),  # Центрируем класс
        ('ALIGN', (6, 0), (6, -1), 'CENTER'),  # Центрируем роль
        ('FONTNAME', (0, 0), (-1, 0), 'RussianFont-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'RussianFont'),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
    ]))
    
    elements.append(table)
    
    # Собираем PDF
    doc.build(elements)


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Загрузка Excel файла и чтение данных гостей"""
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'Неверный формат файла. Требуется .xlsx или .xls'}), 400
    
    # Сохраняем файл
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'guests.xlsx')
    file.save(filepath)
    
    # Читаем данные
    try:
        guests = read_excel_file(filepath)
        return jsonify({'success': True, 'guests': guests})
    except Exception as e:
        return jsonify({'error': f'Ошибка чтения файла: {str(e)}'}), 500


@app.route('/generate-preview', methods=['POST'])
def generate_preview_route():
    """Генерация PDF для предпросмотра"""
    try:
        data = request.json
        rooms = data.get('rooms', [])
        
        if not rooms:
            return jsonify({'error': 'Нет данных о номерах'}), 400
        
        # Генерируем файл для предпросмотра (всегда один и тот же)
        filename = 'preview.pdf'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        # Генерируем PDF
        generate_pdf(rooms, output_path)
        
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации PDF: {str(e)}'}), 500


@app.route('/preview/<filename>')
def preview_file(filename):
    """Отображение PDF для предпросмотра"""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    return send_file(filepath, mimetype='application/pdf')


@app.route('/generate-pdf', methods=['POST'])
def generate_pdf_route():
    """Генерация PDF с распределением по номерам"""
    try:
        data = request.json
        rooms = data.get('rooms', [])
        
        if not rooms:
            return jsonify({'error': 'Нет данных о номерах'}), 400
        
        # Генерируем имя файла
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'room_distribution_{timestamp}.pdf'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        # Генерируем PDF
        generate_pdf(rooms, output_path)
        
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации PDF: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Скачивание сгенерированного PDF"""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    return send_file(filepath, as_attachment=True)


@app.route('/generate-gai-preview', methods=['POST'])
def generate_gai_preview_route():
    """Генерация PDF для предпросмотра (ГАИ)"""
    try:
        data = request.json
        guests_list = data.get('guests', [])
        route = data.get('route', '')
        
        if not guests_list:
            return jsonify({'error': 'Нет данных об участниках'}), 400
        
        # Генерируем файл для предпросмотра (всегда один и тот же)
        filename = 'preview_gai.pdf'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        # Генерируем PDF
        generate_gai_pdf(guests_list, route, output_path)
        
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации PDF: {str(e)}'}), 500


@app.route('/generate-gai-pdf', methods=['POST'])
def generate_gai_pdf_route():
    """Генерация PDF списка для ГАИ"""
    try:
        data = request.json
        guests_list = data.get('guests', [])
        route = data.get('route', '')
        
        if not guests_list:
            return jsonify({'error': 'Нет данных об участниках'}), 400
        
        # Генерируем имя файла
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'gai_list_{timestamp}.pdf'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        # Генерируем PDF
        generate_gai_pdf(guests_list, route, output_path)
        
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации PDF: {str(e)}'}), 500


def generate_gai_pdf(guests_list, route, output_path):
    """Генерирует PDF список для ГАИ"""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []
    
    # Создаём стили с русским шрифтом
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='RussianFont-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='RussianFont',
        fontSize=11,
        textColor=colors.HexColor('#333333')
    )
    
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=normal_style,
        fontSize=8.5,
        leading=10
    )
    
    # Заголовок
    title = Paragraph("Список пассажиров", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # Маршрут
    if route:
        route_text = f"Маршрут: {route}"
        route_para = Paragraph(route_text, normal_style)
        elements.append(route_para)
        elements.append(Spacer(1, 0.5*cm))
    
    # Статистика
    total_guests = len(guests_list)
    students = len([g for g in guests_list if g.get('status', g.get('role', '')) == 'Ученик'])
    teachers = len([g for g in guests_list if g.get('status', g.get('role', '')) == 'Учитель'])
    
    stats_text = f"Всего пассажиров: {total_guests} (учеников: {students}, учителей: {teachers})"
    stats_para = Paragraph(stats_text, normal_style)
    elements.append(stats_para)
    elements.append(Spacer(1, 1*cm))
    
    # Собираем таблицу
    table_data = [['№', 'ФИО', 'Дата рождения', 'Контакт родителя', 'Класс', 'Статус']]
    
    for idx, guest in enumerate(guests_list, 1):
        table_data.append([
            str(idx),
            Paragraph(guest['full_name'], cell_style),
            guest['birth_date'],
            Paragraph(guest['parent_contact'], cell_style),
            guest.get('class', '-'),
            guest.get('status', guest.get('role', 'Ученик'))
        ])
    
    # Создаём таблицу
    table = Table(table_data, colWidths=[1*cm, 4.5*cm, 2.5*cm, 4*cm, 1.5*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (4, 0), (4, -1), 'CENTER'),
        ('ALIGN', (5, 0), (5, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'RussianFont-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'RussianFont'),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    
    elements.append(table)
    
    # Собираем PDF
    doc.build(elements)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
