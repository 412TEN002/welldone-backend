import csv
from typing import Dict, Set

from sqlalchemy import create_engine
from sqlmodel import Session, select

from core.enums import TipType
from models.common import (
    Ingredient,
    CookingTool,
    CookingSetting,
    CookingSettingTip,
)


def convert_time_to_seconds(time_str: str) -> str:
    """
    Convert time string (MM:SS) to seconds
    """
    try:
        minutes, seconds = map(int, time_str.split(':'))
        return str(minutes * 60 + seconds)
    except ValueError:
        return time_str


def parse_csv_to_cooking_settings(file_path: str):
    """
    Parse CSV file and convert to cooking settings data structure
    """
    cooking_settings_data = []

    # Read the CSV file
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        # Skip the header row
        next(csvfile)

        # Read the rows
        reader = csv.reader(csvfile)

        # Group rows by ingredient and cooking tool
        grouped_rows = {}

        for row in reader:
            if len(row) < 7:  # Skip any incomplete rows
                continue

            ingredient, cooking_tool = row[0], row[1]
            key = (ingredient, cooking_tool)

            if key not in grouped_rows:
                grouped_rows[key] = {
                    'ingredient': ingredient,
                    'cooking_tool': cooking_tool,
                    'temperature': row[2],
                    'cooking_time': convert_time_to_seconds(row[3]),
                    'tips': []
                }

            # Collect tips
            tip_types = [TipType.PREPARATION, TipType.COOKING, TipType.FINISHING]
            for i, tip_type in enumerate([row[4], row[5], row[6]]):
                if tip_type.strip():
                    grouped_rows[key]['tips'].append({
                        'tip_type': tip_types[i],
                        'message': tip_type.strip()
                    })

        # Convert to list
        cooking_settings_data = list(grouped_rows.values())

    return cooking_settings_data


cooking_settings_data = parse_csv_to_cooking_settings('./scripts/cooking_settings.csv')


def validate_data_exists(session: Session) -> tuple[bool, Dict[str, Set[str]]]:
    """
    데이터베이스에 필요한 데이터가 존재하는지 검증

    Returns:
        tuple: (검증 통과 여부, 없는 데이터 목록)
    """
    # 데이터베이스에서 현재 존재하는 데이터 조회
    existing_ingredients = {i.name for i in session.exec(select(Ingredient))}
    existing_tools = {t.name for t in session.exec(select(CookingTool))}

    # 데이터에서 필요한 값들 추출
    required_ingredients = {data["ingredient"] for data in cooking_settings_data}
    required_tools = {data["cooking_tool"] for data in cooking_settings_data}

    # 없는 데이터 찾기
    missing_data = {
        "ingredients": required_ingredients - existing_ingredients,
        "cooking_tools": required_tools - existing_tools,
    }

    # 모든 데이터가 존재하는지 확인
    all_exists = all(len(missing) == 0 for missing in missing_data.values())

    return all_exists, missing_data


def seed_cooking_settings(session: Session):
    # 데이터 존재 여부 검증
    all_exists, missing_data = validate_data_exists(session)
    if not all_exists:
        print("필요한 데이터가 데이터베이스에 없습니다:")
        for category, items in missing_data.items():
            if items:
                print(f"- {category}: {', '.join(items)}")
        return False

    # 기존 매핑 데이터 가져오기
    ingredients = {i.name: i.id for i in session.exec(select(Ingredient))}
    cooking_tools = {t.name: t.id for t in session.exec(select(CookingTool))}

    try:
        # Process each setting
        for idx, data in enumerate(cooking_settings_data, 1):
            print(f"처리 중 ({idx}/{len(cooking_settings_data)}): {data['ingredient']}")

            setting = CookingSetting(
                ingredient_id=ingredients[data["ingredient"]],
                cooking_tool_id=cooking_tools[data["cooking_tool"]],
                temperature=(
                    int(data["temperature"]) if data.get("temperature") else None
                ),
                cooking_time=(
                    int(data["cooking_time"]) if data.get("cooking_time") else None
                ),
            )
            session.add(setting)
            session.flush()  # Get setting.id

            # Add tips
            for tip in data.get("tips", []):
                if tip.get('message', '').strip():
                    tip_obj = CookingSettingTip(
                        cooking_setting_id=setting.id, message=tip['message'], tip_type=tip['tip_type']
                    )
                    session.add(tip_obj)

        session.commit()
        print("모든 조리 설정이 성공적으로 추가되었습니다.")
        return True

    except Exception as e:
        session.rollback()
        print(f"데이터 추가 중 오류 발생: {str(e)}")
        return False


if __name__ == "__main__":
    # SQLite database URL
    engine = create_engine(
        "sqlite:///test.db", connect_args={"check_same_thread": False}
    )

    with Session(engine) as session:
        seed_cooking_settings(session)
