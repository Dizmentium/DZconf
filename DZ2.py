import json
import subprocess
import argparse
from pathlib import Path


class DependencyVisualizer:
    def __init__(self, package_name, repo_url, output_path, graph_tool_path):
        self.package_name = package_name
        self.repo_url = repo_url
        self.output_path = Path(output_path)
        self.graph_tool_path = Path(graph_tool_path)
        self.dependencies = {}

    def fetch_dependencies(self):
        # Имитация загрузки package.json и package-lock.json из репозитория
        # В реальном проекте можно использовать `git clone` и `os.walk`.
        try:
            with open("example/package.json", "r") as f:
                package_data = json.load(f)
            with open("example/package-lock.json", "r") as f:
                lock_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("package.json or package-lock.json not found in the specified repository!")

        if self.package_name not in lock_data.get("dependencies", {}):
            raise ValueError(f"Package {self.package_name} not found in dependencies.")

        # Построение графа зависимостей
        self.dependencies = self._parse_dependencies(self.package_name, lock_data["dependencies"])

    def _parse_dependencies(self, package_name, all_dependencies, visited=None):
        if visited is None:
            visited = set()
        if package_name in visited:
            return {}

        visited.add(package_name)
        package_info = all_dependencies.get(package_name, {})
        result = {package_name: {}}

        for dep in package_info.get("requires", {}).keys():
            result[package_name][dep] = self._parse_dependencies(dep, all_dependencies, visited)

        return result

    def generate_mermaid_graph(self):
        def build_mermaid(node, prefix=""):
            lines = []
            for dependency, subdependencies in node.items():
                lines.append(f"{prefix}[{dependency}]")
                for subdependency in subdependencies:
                    lines.append(f"{prefix}[{dependency}] --> {subdependency}")
                    lines.extend(build_mermaid(subdependencies[subdependency], prefix))
            return lines

        lines = build_mermaid(self.dependencies)
        return f"graph TD\n" + "\n".join(lines)

    def save_graph_to_png(self, mermaid_graph):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Сохранение графа в промежуточный файл Mermaid
        temp_mermaid_file = self.output_path.with_suffix(".mmd")
        with open(temp_mermaid_file, "w") as f:
            f.write(mermaid_graph)

        # Генерация PNG через указанный инструмент визуализации
        result = subprocess.run(
            [self.graph_tool_path, "-i", temp_mermaid_file, "-o", self.output_path],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Error generating graph: {result.stderr}")
        print(f"Graph saved to {self.output_path}")

    def visualize(self):
        self.fetch_dependencies()
        mermaid_graph = self.generate_mermaid_graph()
        self.save_graph_to_png(mermaid_graph)


def main():
    parser = argparse.ArgumentParser(description="Dependency Graph Visualizer")
    parser.add_argument("graph_tool_path", help="Path to the graph visualization tool")
    parser.add_argument("package_name", help="Name of the package to analyze")
    parser.add_argument("output_path", help="Path to save the generated graph")
    parser.add_argument("repo_url", help="URL of the repository to analyze")

    args = parser.parse_args()

    visualizer = DependencyVisualizer(
        package_name=args.package_name,
        repo_url=args.repo_url,
        output_path=args.output_path,
        graph_tool_path=args.graph_tool_path,
    )
    visualizer.visualize()


if __name__ == "__main__":
    main()
    
#ТЕСТЫ

"""import unittest
from dependency_visualizer import DependencyVisualizer

class TestDependencyParser(unittest.TestCase):
    def setUp(self):
        self.visualizer = DependencyVisualizer(
            package_name="example-package",
            repo_url="https://example.com/repo.git",
            output_path="output/dependencies.png",
            graph_tool_path="/path/to/graph_tool",
        )
        with open("example/package-lock.json") as f:
            self.lock_data = json.load(f)

    def test_fetch_dependencies(self):
        self.visualizer._parse_dependencies("example-package", self.lock_data["dependencies"])
        self.assertIn("example-package", self.visualizer.dependencies)
        self.assertIn("some-dependency", self.visualizer.dependencies["example-package"])
##Анализ зависимости
class TestGraphGeneration(unittest.TestCase):
    def setUp(self):
        self.visualizer = DependencyVisualizer(
            package_name="example-package",
            repo_url="https://example.com/repo.git",
            output_path="output/dependencies.png",
            graph_tool_path="/path/to/graph_tool",
        )
        self.visualizer.dependencies = {
            "example-package": {
                "dep1": {"subdep1": {}, "subdep2": {}},
                "dep2": {},
            }
        }

    def test_generate_mermaid_graph(self):
        mermaid_graph = self.visualizer.generate_mermaid_graph()
        self.assertIn("example-package --> dep1", mermaid_graph)
        self.assertIn("dep1 --> subdep1", mermaid_graph)"""