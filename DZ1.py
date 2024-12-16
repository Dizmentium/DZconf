import os
import tarfile
import argparse
import time

class ShellEmulator:
    def __init__(self, tar_path):
        self.root = "/"
        self.current_dir = "/"
        self.fs = {}
        self.start_time = time.time()
        self.load_tar(tar_path)

    def load_tar(self, tar_path):
        with tarfile.open(tar_path, "r") as tar:
            for member in tar.getmembers():
                self.fs[member.name] = {"type": "dir" if member.isdir() else "file", "size": member.size}

    def ls(self):
        for item in self.fs:
            if item.startswith(self.current_dir) and item != self.current_dir:
                print(item.replace(self.current_dir, "").strip("/"))

    def cd(self, path):
        if path == "..":
            self.current_dir = os.path.dirname(self.current_dir)
        elif path in self.fs and self.fs[path]["type"] == "dir":
            self.current_dir = path
        else:
            print(f"No such directory: {path}")

    def du(self):
        total_size = sum(info["size"] for path, info in self.fs.items() if path.startswith(self.current_dir))
        print(f"Total size of {self.current_dir}: {total_size} bytes")

    def uptime(self):
        uptime = time.time() - self.start_time
        print(f"Uptime: {uptime:.2f} seconds")

    def exit(self):
        print("Exiting shell...")
        raise SystemExit

def main():
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument("tar_path", help="Path to tar archive")
    args = parser.parse_args()

    emulator = ShellEmulator(args.tar_path)

    while True:
        try:
            command = input(f"{emulator.current_dir}> ").strip()
            if command == "ls":
                emulator.ls()
            elif command.startswith("cd"):
                _, path = command.split(maxsplit=1)
                emulator.cd(path)
            elif command == "du":
                emulator.du()
            elif command == "uptime":
                emulator.uptime()
            elif command == "exit":
                emulator.exit()
            else:
                print(f"Unknown command: {command}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()

#ТЕСТЫ

"""import unittest
from emulator import ShellEmulator

class TestLs(unittest.TestCase):
    def setUp(self):
        self.emulator = ShellEmulator("virtual_fs.tar")

    def test_ls_root(self):
        self.emulator.current_dir = "/"
        self.assertIn("file1.txt", self.emulator.ls())

    def test_ls_subdir(self):
        self.emulator.current_dir = "/subdir"
        self.assertIn("file2.txt", self.emulator.ls())
class TestCd(unittest.TestCase):
    def setUp(self):
        self.emulator = ShellEmulator("virtual_fs.tar")

    def test_cd_valid(self):
        self.emulator.cd("/subdir")
        self.assertEqual(self.emulator.current_dir, "/subdir")

    def test_cd_invalid(self):
        self.emulator.cd("/nonexistent")
        self.assertNotEqual(self.emulator.current_dir, "/nonexistent")"""