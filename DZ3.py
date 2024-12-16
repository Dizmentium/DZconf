import re
import argparse
import toml


class ConfigConverter:
    def __init__(self, input_file):
        self.input_file = input_file
        self.variables = {}

    def parse_config(self):
        """
        Парсинг учебного конфигурационного языка.
        """
        with open(self.input_file, 'r') as f:
            lines = f.readlines()

        config_data = {}
        current_scope = config_data

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):  # Пропуск комментариев и пустых строк
                continue

            # Объявление переменной
            if match := re.match(r"def\s+([_a-zA-Z][_a-zA-Z0-9]*)\s*:=\s*(.*)", line):
                name, value = match.groups()
                self.variables[name] = self._evaluate_expression(value)
                continue

            # Вставка константного выражения
            if line.startswith("#[") and line.endswith("]"):
                expression = line[2:-1].strip()
                evaluated_value = self._evaluate_expression(expression)
                current_scope.append(evaluated_value)
                continue

            # Обработка словарей
            if line.startswith("{") and line.endswith("}"):
                dictionary = self._parse_dictionary(line)
                current_scope = dictionary
                continue

            # Обработка массивов
            if line.startswith("<<") and line.endswith(">>"):
                array = self._parse_array(line)
                current_scope = array
                continue

            raise ValueError(f"Syntax error: {line}")

        return config_data

    def _parse_dictionary(self, line):
        """
        Парсинг словарей.
        """
        dictionary = {}
        pairs = line.strip("{}").split(",")
        for pair in pairs:
            key, value = map(str.strip, pair.split(":"))
            dictionary[key] = self._evaluate_expression(value)
        return dictionary

    def _parse_array(self, line):
        """
        Парсинг массивов.
        """
        elements = line.strip("<<>>").split(",")
        return [self._evaluate_expression(element.strip()) for element in elements]

    def _evaluate_expression(self, expression):
        """
        Вычисление выражений на этапе трансляции.
        """
        # Обработка простых чисел
        if re.match(r"^\d+$", expression):
            return int(expression)

        # Обработка переменных
        if expression in self.variables:
            return self.variables[expression]

        # Обработка функций и операций
        if "+" in expression or "-" in expression:
            return eval(expression, {}, self.variables)

        if "concat" in expression:
            match = re.match(r"concat\((.*)\)", expression)
            if match:
                args = match.group(1).split(",")
                return "".join(map(str.strip, args))

        raise ValueError(f"Invalid expression: {expression}")

    def convert_to_toml(self, data):
        """
        Преобразование словаря в TOML.
        """
        return toml.dumps(data)


def main():
    parser = argparse.ArgumentParser(description="Учебный конфигурационный язык в TOML")
    parser.add_argument("input_file", help="Путь к файлу конфигурации")
    args = parser.parse_args()

    converter = ConfigConverter(input_file=args.input_file)
    try:
        config_data = converter.parse_config()
        toml_output = converter.convert_to_toml(config_data)
        print(toml_output)
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
    
#ТЕСТЫ

"""import unittest
from config_converter import ConfigConverter


class TestConfigParser(unittest.TestCase):
    def setUp(self):
        self.converter = ConfigConverter(input_file="examples/example1.cfg")

    def test_parse_array(self):
        result = self.converter._parse_array("<< 1, 2, 3 >>")
        self.assertEqual(result, [1, 2, 3])

    def test_parse_dictionary(self):
        result = self.converter._parse_dictionary("{ key1 : 1, key2 : 2 }")
        self.assertEqual(result, {"key1": 1, "key2": 2})

    def test_evaluate_expression(self):
        self.converter.variables = {"x": 10}
        self.assertEqual(self.converter._evaluate_expression("x + 1"), 11)
        self.assertEqual(self.converter._evaluate_expression("concat('a', 'b')"), "ab")"""