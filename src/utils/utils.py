# 한글 유니코드 범위
CHOSUNG_START_LETTER = 4352
JAMO_START_LETTER = 44032
JAMO_END_LETTER = 55203
JAMO_CYCLES = 588

# 초성 리스트
CHOSUNG_LIST = [
    "ㄱ",
    "ㄲ",
    "ㄴ",
    "ㄷ",
    "ㄸ",
    "ㄹ",
    "ㅁ",
    "ㅂ",
    "ㅃ",
    "ㅅ",
    "ㅆ",
    "ㅇ",
    "ㅈ",
    "ㅉ",
    "ㅊ",
    "ㅋ",
    "ㅌ",
    "ㅍ",
    "ㅎ",
]


def get_chosung(text: str) -> str:
    """
    한글 문자열의 초성을 추출합니다.
    """
    result = []
    for char in text:
        if "가" <= char <= "힣":
            char_code = ord(char) - JAMO_START_LETTER
            char_code = char_code // JAMO_CYCLES
            result.append(CHOSUNG_LIST[char_code])
        else:
            result.append(char)
    return "".join(result)


def is_chosung(keyword: str) -> bool:
    """
    문자열이 초성으로만 이루어져 있는지 확인합니다.
    """
    return all(char in CHOSUNG_LIST for char in keyword)
