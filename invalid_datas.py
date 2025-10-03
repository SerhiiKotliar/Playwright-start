invalid_urls = [
    "ftp://example.com",         # 1. неверная схема
    "example.com",               # 2. отсутствует схема
    "http:/example.com",         # 3. схема с одним слэшем
    "http://examplecom",         # 4. нет точки в домене
    "http://example.c",          # 5. TLD слишком короткий
    "http://example.c0m",        # 6. TLD с цифрой
    "http://exa!mple.com",       # 7. недопустимый символ в домене
    "http://example.com:ab12",   # 8. порт с буквами
    "http://example.com:",       # 9. пустой порт
    "http://example.com/pa th",  # 10. пробел в пути
    "http://example.com/?q=te st",  # 11. пробел в query
    "http://example.com/#frag ment", # 12. пробел в фрагменте
    "http://:8080/"              # 13. отсутствует домен
]

invalid_emails = [
    "plainaddress",          # 1. нет символа @
    "@domain.com",           # 2. отсутствует локальная часть
    "user@",                 # 3. отсутствует домен после @
    "user@.com",             # 4. домен начинается с точки
    "user@domain",           # 5. нет точки после домена
    "user@domain.",          # 6. точка в конце без TLD
    "user@do main.com",      # 7. пробел в домене
    "us er@domain.com",      # 8. пробел в локальной части
    "user@@domain.com",      # 9. два символа @
    "user@domain..com",      # 10. двойная точка в домене
    ".user@domain.com",      # 11. локальная часть начинается с точки
    "user.@domain.com",      # 12. локальная часть оканчивается точкой
    "user@-domain.com",      # 13. домен начинается с дефиса
    "user@domain-.com",      # 14. домен оканчивается дефисом
    "user@domain.c",         # 15. TLD слишком короткий (1 символ)
    "user@domain,com",       # 16. запятая вместо точки
    "user@domain#.com",      # 17. недопустимый символ # в домене
    "user name@domain.com",  # 18. пробел в адресе
]
