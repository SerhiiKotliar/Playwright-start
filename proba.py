import re


def allows_special_chars(pattern: str) -> bool:
    """
    Возвращает True, если паттерн разрешает спецсимволы (не буквы и цифры).
    """

    # Сначала проверяем lookahead/lookbehind на наличие \W или специальных символов
    lookahead_matches = re.finditer(r"\(\?[=!<](.*?)\)", pattern)
    for match in lookahead_matches:
        lookahead_content = match.group(1)
        # Проверяем на \W в lookahead
        if "\\W" in lookahead_content:
            return True
        # Проверяем на специальные символы в классах внутри lookahead
        lookahead_class_matches = re.finditer(r"\[(.*?)\]", lookahead_content)
        for class_match in lookahead_class_matches:
            inside = class_match.group(1)
            if contains_special_char_in_class(inside):
                return True

    # Удаляем lookahead/lookbehind утверждения для дальнейшего анализа
    pattern_clean = re.sub(r"\(\?[=!<].*?\)", "", pattern)

    # Проверка на \W или . вне классов
    in_class = False
    escaped = False
    i = 0
    while i < len(pattern_clean):
        ch = pattern_clean[i]

        if not escaped:
            if ch == "\\":
                escaped = True
                # Проверяем \W (но не \w, \d, \s и т.д.)
                if i + 1 < len(pattern_clean) and pattern_clean[i + 1] == "W":
                    return True
            elif ch == "[":
                in_class = True
            elif ch == "]":
                in_class = False
            elif ch == "." and not in_class:
                return True
        else:
            escaped = False

        i += 1

    # Проверка классов символов [ ... ]
    for m in re.finditer(r"\[(.*?)\]", pattern_clean):
        inside = m.group(1)

        # Обрабатываем escape-последовательности внутри класса
        inside_clean = ""
        j = 0
        while j < len(inside):
            c = inside[j]
            if c == "\\":
                if j + 1 < len(inside):
                    next_char = inside[j + 1]
                    # Если это \W - точно разрешает спецсимволы
                    if next_char == "W":
                        return True
                    # Если это \w, \d, \s - пропускаем (это буквы/цифры/пробелы)
                    elif next_char in "wds":
                        inside_clean += next_char
                        j += 1
                    else:
                        # Другие escape-последовательности могут быть спецсимволами
                        return True
                j += 1
            else:
                inside_clean += c
                j += 1

        # отрицательный класс [^...]
        if inside_clean.startswith("^"):
            excluded = inside_clean[1:]
            # Если исключаются ТОЛЬКО буквы и цифры (и возможно диапазоны между ними),
            # то разрешаются спецсимволы
            if all_characters_are_alnum(excluded):
                return True
        # положительный класс [ ... ]
        else:
            # Если есть хотя бы один явный не-буквенно-цифровой символ
            if contains_special_char_in_class(inside_clean):
                return True

    return False


def all_characters_are_alnum(chars: str) -> bool:
    """Проверяет, содержат ли символы только буквы, цифры и их диапазоны."""
    i = 0
    while i < len(chars):
        if chars[i] == '-':
            if i > 0 and i < len(chars) - 1:
                # Проверяем диапазон
                start = chars[i - 1]
                end = chars[i + 1]
                if not (start.isalnum() and end.isalnum() and ord(start) < ord(end)):
                    return False
                i += 2
            else:
                return False
        elif not chars[i].isalnum():
            return False
        else:
            i += 1
    return True


def contains_special_char_in_class(chars: str) -> bool:
    """Проверяет, содержит ли строка специальные символы в классе символов."""
    i = 0
    while i < len(chars):
        if chars[i] == '-':
            if i > 0 and i < len(chars) - 1:
                # Это диапазон, пропускаем
                i += 2
            else:
                # Одиночный '-' - это специальный символ
                return True
        elif not chars[i].isalnum() and chars[i] not in '^':
            # Найден специальный символ (кроме ^ в начале)
            return True
        else:
            i += 1
    return False

#
# # Тесты
# tests = [
#     (r"^[A-Za-z0-9]{4,12}$", False),
#     (r"(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", False),
#     (r"(?=.*[A-Za-z])(?=.*\W)[A-Za-z0-9]", True),  # Этот теперь должен работать правильно
#     (r"(?=.*[A-Za-z])(?=.*[@#])[A-Za-z@#]{8,}$", True),
#     (r"(?=.*[A-Za-z])[A-Za-z](?=.*\d)[0-9](?=.*[!@\#\$%\^\&\*\(\)_=\+\[\]\{\};:,\.<>/\?\\\|\-])[!@\#\$%\^\&\*\(\)_=\+\[\]\{\};:,\.<>/\?\\\|\-]{4,20}$",
#      True),
#     (r"[^A-Za-z0-9]", True),
#     (r"[A-Za-z]", False),
#     (r"[A-Za-z_]", True),
#     (r"^[A-Za-z0-9]{4,12}$", False),
#     (r"[\dA-Z]", False),  # Только цифры и буквы
#     (r"[0-9A-Z]", False),  # Только цифры и буквы (диапазоны)
#     (r"[0-9A-Z_]", True),  # Содержит _
#     (r"(?=.*[A-Z])(?=.*[!@#$])[A-Za-z0-9!@#$]", True),  # Lookahead с спецсимволами
# ]
#
# print("Тестирование исправленной функции:")
# for p, exp in tests:
#     result = allows_special_chars(p)
#     status = "✓" if result == exp else "✗"
#     print(f"{status} {p}\n  -> {result} (ожидалось {exp})")
# print(allows_special_chars(r"^[A-Za-z0-9]{4,12}$"))
# print(allows_special_chars(r"^(?=.*[A-Za-z])[A-Za-z](?=.*\d)[0-9](?=.*[!@\#\$%\^\&\*\(\)_=\+\[\]\{\};:,\.<>/\?\\\|\-])[!@\#\$%\^\&\*\(\)_=\+\[\]\{\};:,\.<>/\?\\\|\-]{4,20}$"))
# print(allows_special_chars(r"(?=.*[A-Za-z])[A-Za-z](?=.*\d)[0-9](?=.*[!@\#\$%\^\&\*\(\)_=\+\[\]\{\};:,\.<>/\?\\\|\-])[!@\#\$%\^\&\*\(\)_=\+\[\]\{\};:,\.<>/\?\\\|\-]{4,20}$"))
#
