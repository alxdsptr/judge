import argparse
from log import ILogger, TermLogger, JsonLogger
from judge import prepare, build, test as test_by_case
from cases import get_cases


def judge(path: str, logger: ILogger):
    # if logger.exec_func(prepare, path):
    if logger.exec_func(build, path):
        for case in get_cases():
            def test(p: str):
                return test_by_case(p, case)
            logger.exec_func(test, path)
    logger.end()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='RJSJ Mini-lisp Homework Judge Program')
    parser.add_argument('workspaces', nargs='*', help='workspace path')
    parser.add_argument('--batch', dest='batch_file',
                        help='a file containing a list of workspace paths')
    parser.add_argument('--output', dest='output_file',
                        help='a file to save the judge result')

    args = parser.parse_args()

    if args.output_file:
        logger = JsonLogger(args.output_file)
    else:
        logger = TermLogger()

    if args.batch_file:
        with open(args.batch_file, "r") as f:
            for line in f:
                judge(line.strip(), logger)
    else:
        for arg in args.workspaces:
            judge(arg, logger)
