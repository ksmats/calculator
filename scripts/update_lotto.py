#!/usr/bin/env python3
"""
로또 당첨번호 자동 갱신 스크립트
- 최신 전체 회차 데이터를 받아와서
- 계산기 HTML 파일 안의 LOTTO_DATA / footer 문구를 최신 데이터로 교체한다.
"""
import json
import re
import sys
import urllib.request

# 파일명이 한글이면 리포지토리 루트에서 실제 파일명을 정확히 맞춰주세요.
HTML_PATH = "로또번호생성기.html"
DATA_URL = "https://raw.githubusercontent.com/smok95/lotto/main/results/all.json"


def fetch_latest_data():
    req = urllib.request.Request(DATA_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        raw = json.loads(res.read().decode("utf-8"))
    trimmed = [
        {"n": d["draw_no"], "w": d["numbers"], "b": d["bonus_no"], "d": d["date"][:10]}
        for d in raw
    ]
    return trimmed


def update_html(trimmed):
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    data_str = json.dumps(trimmed, ensure_ascii=False, separators=(",", ":"))
    latest = trimmed[-1]

    new_html, n1 = re.subn(
        r"const LOTTO_DATA = \[.*?\];",
        "const LOTTO_DATA = " + data_str + ";",
        html,
        count=1,
        flags=re.DOTALL,
    )
    if n1 == 0:
        print("경고: LOTTO_DATA 패턴을 찾지 못했습니다. HTML 구조가 바뀐 것 같습니다.", file=sys.stderr)
        sys.exit(1)

    new_html = re.sub(
        r"1회 ~ \d+회 \(\d{4}-\d{2}-\d{2}\)",
        f"1회 ~ {latest['n']}회 ({latest['d']})",
        new_html,
    )

    if new_html == html:
        print("변경 사항 없음 (이미 최신 데이터)")
        return False

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"업데이트 완료: 최신 {latest['n']}회 ({latest['d']}), 총 {len(trimmed)}회차")
    return True


if __name__ == "__main__":
    data = fetch_latest_data()
    changed = update_html(data)
    with open("/tmp/lotto_changed.txt", "w") as f:
        f.write("true" if changed else "false")
