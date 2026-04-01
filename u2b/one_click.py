import argparse
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = BASE_DIR / "runtime"
COOKIES_PATH = BASE_DIR / "cookies.json"
BILIUP_BIN = BASE_DIR / ("biliup.exe" if os.name == "nt" else "biliup")


def ensure_ready() -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    if not BILIUP_BIN.exists():
        raise FileNotFoundError(
            f"未找到投稿工具: {BILIUP_BIN}\n"
            "请先在 u2b 目录执行 `bash setup.sh`，并确认 biliup 可执行文件存在。"
        )
    if not COOKIES_PATH.exists():
        raise FileNotFoundError(
            f"未找到登录态文件: {COOKIES_PATH}\n"
            "请先执行 `./biliup login` 生成 cookies.json。"
        )


def run_pipeline(*, single_url: str | None, input_file: str | None, tid: int) -> None:
    if bool(single_url) == bool(input_file):
        raise ValueError("请二选一：使用 `--single` 或 `--input`。")

    try:
        import new_downloader
    except ModuleNotFoundError as exc:
        missing_name = getattr(exc, "name", "") or "unknown"
        raise RuntimeError(
            "缺少 Python 依赖，无法启动一键流程。\n"
            f"未安装模块: {missing_name}\n"
            "请在 u2b 目录执行:\n"
            "  python3 -m pip install -r requirements.txt"
        ) from exc

    ensure_ready()
    if single_url:
        print("开始一键流程：下载 -> 转封面 -> 投稿 B 站")
        new_downloader.main(single_url, tid)
        return

    print("开始批量一键流程：下载 -> 转封面 -> 投稿 B 站")
    new_downloader.process_url_file(input_file, tid)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="一键完成 YouTube 下载并投稿到 B 站")
    parser.add_argument("-s", "--single", help="单个 YouTube 视频 URL")
    parser.add_argument("-i", "--input", help="URL 列表文件路径（每行一个 URL）")
    parser.add_argument("-t", "--tid", type=int, default=194, help="B 站分区 ID（默认 194）")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        run_pipeline(single_url=args.single, input_file=args.input, tid=args.tid)
        return 0
    except Exception as exc:
        print(f"[one-click error] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
