from pathlib import Path


def read_document(path):
    return Path(path).read_text(encoding="utf-8").splitlines()


if __name__ == "__main__":
    for line in read_document("tests/fixtures/test contract.txt"):
        print(line)