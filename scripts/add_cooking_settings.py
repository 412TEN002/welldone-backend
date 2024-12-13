from typing import Dict, Set

from sqlalchemy import create_engine
from sqlmodel import Session, select

from models.common import (
    Ingredient,
    CookingMethod,
    CookingTool,
    HeatingMethod,
    CookingSetting,
    CookingSettingTip,
)

cooking_settings_data = [
    {
        "ingredient": "가지",
        "cooking_method": "찌기",
        "cooking_tool": "냄비 / 프라이팬",
        "heating_method": "인덕션 / 가스레인지",
        "temperature": "6",
        "cooking_time": "180",
        "tips": [
            "가지는 깨끗이 씻어 2cm 두께로 동글하게 썰어주세요.",
            "예열된 팬에 기름을 두르고 중간 불에서 앞뒤로 노릇하게 구워주세요.",
            "너무 오래 구우면 가지가 질겨질 수 있어요.",
        ],
    }
]


def validate_data_exists(session: Session) -> tuple[bool, Dict[str, Set[str]]]:
    """
    데이터베이스에 필요한 데이터가 존재하는지 검증

    Returns:
        tuple: (검증 통과 여부, 없는 데이터 목록)
    """
    # 데이터베이스에서 현재 존재하는 데이터 조회
    existing_ingredients = {i.name for i in session.exec(select(Ingredient))}
    existing_methods = {m.name for m in session.exec(select(CookingMethod))}
    existing_tools = {t.name for t in session.exec(select(CookingTool))}
    existing_heating_methods = {h.name for h in session.exec(select(HeatingMethod))}

    # 데이터에서 필요한 값들 추출
    required_ingredients = {data["ingredient"] for data in cooking_settings_data}
    required_methods = {data["cooking_method"] for data in cooking_settings_data}
    required_tools = {data["cooking_tool"] for data in cooking_settings_data}
    required_heating_methods = {
        data["heating_method"] for data in cooking_settings_data
    }

    # 없는 데이터 찾기
    missing_data = {
        "ingredients": required_ingredients - existing_ingredients,
        "cooking_methods": required_methods - existing_methods,
        "cooking_tools": required_tools - existing_tools,
        "heating_methods": required_heating_methods - existing_heating_methods,
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
    cooking_methods = {m.name: m.id for m in session.exec(select(CookingMethod))}
    cooking_tools = {t.name: t.id for t in session.exec(select(CookingTool))}
    heating_methods = {h.name: h.id for h in session.exec(select(HeatingMethod))}

    try:
        # Process each setting
        for idx, data in enumerate(cooking_settings_data, 1):
            print(f"처리 중 ({idx}/{len(cooking_settings_data)}): {data['ingredient']}")

            setting = CookingSetting(
                ingredient_id=ingredients[data["ingredient"]],
                cooking_method_id=cooking_methods[data["cooking_method"]],
                cooking_tool_id=cooking_tools[data["cooking_tool"]],
                heating_method_id=heating_methods[data["heating_method"]],
                temperature=(
                    float(data["temperature"]) if data.get("temperature") else None
                ),
                cooking_time=(
                    int(data["cooking_time"]) if data.get("cooking_time") else None
                ),
            )
            session.add(setting)
            session.flush()  # Get setting.id

            # Add tips
            for tip in data.get("tips", []):
                if tip.strip():
                    tip_obj = CookingSettingTip(
                        cooking_setting_id=setting.id, message=tip.strip()
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
