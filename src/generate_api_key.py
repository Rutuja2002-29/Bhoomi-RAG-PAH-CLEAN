import secrets
from pathlib import Path

from dotenv import load_dotenv


def generate_api_key() -> str:
    return secrets.token_urlsafe(32)


def save_api_key(env_path: Path, api_key: str) -> None:
    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    saved = False
    output = []
    for line in lines:
        if line.startswith("API_KEY="):
            output.append(f"API_KEY={api_key}")
            saved = True
        else:
            output.append(line)

    if not saved:
        output.append(f"API_KEY={api_key}")

    env_path.write_text("\n".join(output).strip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    load_dotenv()
    key = generate_api_key()
    save_api_key(Path(".env"), key)
    print(key)
