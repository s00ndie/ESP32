import network
import socket
from machine import Pin

led = Pin(2, Pin.OUT)
led.value(0)

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(ssid='ESP32_Control', password='12345678', authmode=3)

print('Швидкий сервер запущено!')

def web_page():
    led_state = 'ON' if led.value() == 1 else 'OFF'
    color = '#4CAF50' if led.value() == 1 else '#f44336'
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Instant Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial; text-align: center; margin-top: 60px; background: #f4f4f9; }}
        .btn {{ display: inline-block; padding: 18px 35px; font-size: 24px; color: #fff; background: #4CAF50; border: none; border-radius: 12px; margin: 10px; cursor: pointer; }}
        .off {{ background: #f44336; color: #fff; }}
        .status {{ font-weight: bold; color: {color}; font-size: 22px; }}
    </style>
    <script>
        function toggleLed(state) {{
            fetch('/' + state).then(response => response.text()).then(val => {{
                document.getElementById('status').innerText = val;
                document.getElementById('status').style.color = (val === 'ON' ? '#4CAF50' : '#f44336');
            }});
        }}
    </script>
</head>
<body>
    <h1>ESP32 Instant Home</h1>
    <p>Status: <span id="status" class="status">{led_state}</span></p>
    <p><button class="btn" onclick="toggleLed('ledon')">On</button></p>
    <p><button class="btn off" onclick="toggleLed('ledoff')">Off</button></p>
</body>
</html>"""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)

while True:
    conn = None
    try:
        conn, addr = s.accept()
        request = conn.recv(1024)
        request = str(request)
        
        if '/ledon' in request:
            led.value(1)
            response_text = "ON"
        elif '/ledoff' in request:
            led.value(0)
            response_text = "OFF"
        else:
            # Якщо це звичайний запит сторінки
            response_text = web_page()
            conn.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n')
            conn.sendall(response_text)
            conn.close()
            continue

        # Якщо це був AJAX-запит від кнопки, відповідаємо миттєво лише текстом стану
        conn.send('HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n')
        conn.sendall(response_text)
        conn.close()
        
    except OSError:
        if conn:
            conn.close()