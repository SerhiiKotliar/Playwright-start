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


def run_tests():
    """Запуск всех тестов pytest с выводом в allure result"""
    cmd = f"python -m pytest -v -s tests --alluredir {RESULT_DIR}"
    subprocess.run(cmd, shell=True)


def run_allure_serve():
    """Запуск встроенной команды allure serve"""
    cmd = f"allure serve {RESULT_DIR}"
    subprocess.run(cmd, shell=True)


def run_allure_generate_and_open():
    """Генерация отчёта и запуск локального сервера"""
    cmd = f"allure generate {RESULT_DIR} -o {REPORT_DIR} --clean"
    subprocess.run(cmd, shell=True)

    port = find_free_port(START_PORT)

    os.chdir(REPORT_DIR)
    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}/index.html"
        print(f"Сервер запущен: {url}")
        webbrowser.open(url)
        httpd.serve_forever()


def run_all():
    """Запуск тестов, генерация отчёта и сервер"""
    run_tests()
    run_allure_generate_and_open()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "serve":
            run_allure_serve()
        elif sys.argv[1] == "tests":
            run_tests()
        elif sys.argv[1] == "all":
            run_all()
        else:
            print("Неизвестная команда. Используй: tests | serve | generate | all")
    else:
        run_allure_generate_and_open()
