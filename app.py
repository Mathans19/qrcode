from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'attendance'

mysql = MySQL(app)

@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    student_id = data['student_id']
    student_name = data['student_name']
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    
    periods = [
        {"start_time": datetime.strptime('08:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('09:00:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('09:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('10:00:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('10:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('11:00:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('11:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('12:00:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('13:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('14:00:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('14:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('15:00:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('15:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('16:00:00', '%H:%M:%S').time()}
    ]
    
    # Add logic to check if student already marked attendance for the current date
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM attendance WHERE student_id = %s AND date = %s", (student_id, current_date))
    existing_record = cur.fetchone()
    if existing_record:
        # Student already marked attendance for the current date, update attendance for the appropriate period
        for i, period in enumerate(periods, start=1):
            if current_time >= period["start_time"] and current_time <= period["end_time"]:
                cur.execute(f"UPDATE attendance SET period{i} = TRUE WHERE student_id = %s AND date = %s", (student_id, current_date))
                mysql.connection.commit()
                cur.close()
                return jsonify({'message': f'Attendance marked successfully for period {i}'}), 200
        cur.close()
        return jsonify({'message': 'Student already marked attendance for the current date'}), 400
    else:
        # Student not marked attendance for the current date, insert new attendance record
        attendance_values = [True if current_time >= period["start_time"] and current_time <= period["end_time"] else False for period in periods]
        attendance_values.insert(0, student_id)
        attendance_values.insert(1, student_name)
        attendance_values.insert(2, current_date)
        placeholders = ','.join(['%s'] * len(attendance_values))
        # Replace "mark-attendance" with the actual endpoint URL for marking attendance
        query = f"INSERT INTO attendance (student_id, name, date, period1, period2, period3, period4, period5, period6, period7) VALUES ({placeholders})"
        cur.execute(query, tuple(attendance_values))
        mysql.connection.commit()
        cur.close()
        for i, attendance in enumerate(attendance_values[3:], start=1):  # Skip the student_id, name, and date
            if attendance:
                return jsonify({'message': f'Attendance marked successfully for period {i}'}), 200

if __name__ == '__main__':
    app.run(debug=True)
