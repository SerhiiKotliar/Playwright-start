import subprocess
import webbrowser
import http.server
import socketserver
import os
import sys
import socket

RESULT_DIR = "result"
REPORT_DIR = "report"
START_PORT = 8080


def find_free_port(start_port=8080, max_port=9000):
    """Ищет свободный порт начиная с start_port"""
    port = start_port
    while port < max_port:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError("Не удалось найти свободный порт")

def run_tests_allure():
    """Запуск встроенной команды pytest"""
    subprocess.run(["pytest", "-v", "-s", "allure_dir", RESULT_DIR])

def run_allure_serve():
    """Запуск встроенной команды allure serve"""
    subprocess.run(["allure", "serve", RESULT_DIR])


def run_allure_generate_and_open():
    """Генерация отчёта и запуск локального сервера"""
    # Генерация
    subprocess.run(["allure", "generate", RESULT_DIR, "-o", REPORT_DIR, "--clean"])

    # Ищем свободный порт
    port = find_free_port(START_PORT)

    # Запуск сервера Python
    os.chdir(REPORT_DIR)
    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}/index.html"
        print(f"Сервер запущен: {url}")
        webbrowser.open(url)
        httpd.serve_forever()


if __name__ == "__main__":
    run_allure_serve()
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        run_allure_serve()
    else:
        run_allure_generate_and_open()
