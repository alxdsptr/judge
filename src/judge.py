from typing import Union, List, Tuple
from cases import Case
from dataclasses import dataclass
import os
import shutil
import urllib.request
import subprocess
import json


@dataclass
class JudgeResult:
    title: str
    success: bool
    log: str

def prepare(path: str) -> JudgeResult:
    dirname = os.path.dirname(os.path.abspath(__file__))
    shutil.copytree(os.path.join(dirname, "..\\test"), path, dirs_exist_ok=True)

    return JudgeResult("prepare", True, "")

def build(path: str) -> JudgeResult:
    os.chdir(path)

    build_command = "msbuild mini-lisp.sln /p:Configuration=Release /p:Platform=x64"
    build_r = subprocess.run(
        build_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = build_r.stdout.decode(errors="ignore") + \
        build_r.stderr.decode(errors="ignore")
    if build_r.returncode != 0:
        return JudgeResult("build", False, output)

    return JudgeResult("build", True, output)

def run_exe(path: str, args: List[str], output: str, cur_path: str) -> Tuple[bool, int, str]:
    args = [path] + args
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    output = os.path.join(cur_path, output)
    expected_output = open(output, "r", encoding="utf-8")
    e_out = expected_output.read()

    stdout, stderr = proc.communicate()
    exit_code = proc.returncode
    if stdout != e_out:
        return False, 0, f"Output: {stdout}\nExpected: {e_out}"
    return True, exit_code, ' '.join(args) + '\n' + stdout + '\n' + stderr

def run_exe_it(path: str, args: List[str], input: str, output: str, cur_path: str) -> Tuple[bool, int, str]:
    args = [path] + args
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    input = os.path.join(cur_path, input)
    input = open(input, "r", encoding="utf-8")
    output = os.path.join(cur_path, output)
    expected_output = open(output, "r", encoding="utf-8")

    for line in input:
        proc.stdin.write(line)
        proc.stdin.flush()
        e_out = expected_output.readline()
        if e_out == "exit\n":
            break
        elif e_out == "Error\n":
            # check if stderr is empty
            if not proc.stderr.readable():
                proc.kill()
                proc.wait()
                return False, 0, "expected error"
            err = proc.stderr.readline()
            out = proc.stdout.read(4)
            if out != ">>> ":
                proc.kill()
                proc.wait()
                return False, 0, f"Output: {out}\nExpected: >>> "
        else:
            output = proc.stdout.readline()
            if output != e_out:
                proc.kill()
                proc.wait()
                return False, 0, f"Output: {output}\nExpected: {e_out}"

    stdout, stderr = proc.communicate()
    exit_code = proc.returncode
    return True, exit_code, ' '.join(args) + '\n' + stdout + '\n' + stderr


def test(path: str, case: Case) -> JudgeResult:
    os.chdir(path)
    exe_path = os.path.join(
        path, "bin", "x64", "Release", "mini_lisp.exe")
    cur_file_path = os.path.abspath(__file__)
    cur_path = os.path.dirname(cur_file_path)
    if not os.path.exists(exe_path):
        return JudgeResult("pretest", False, "Output executable file mini_lisp does not exist.")
    args = case.generate_args(cur_path)
    if case.file_mode:
        success, code, log = run_exe(exe_path, args, case.output, cur_path)
    else:
        success, code, log = run_exe_it(exe_path, args, case.input, case.output, cur_path)
    if not success:
        return JudgeResult("test", False, log)

    if code != case.exit_code:
        return JudgeResult("test", False, f"Program unexpectedly exited with code {code}.\nOutput:\n{log}")
    return JudgeResult("test", True, log)