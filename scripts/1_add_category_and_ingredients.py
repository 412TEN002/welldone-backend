from sqlmodel import Session, create_engine

from core.enums import ColorTheme
from models.common import Category, Ingredient, NutritionTag, IngredientNutritionLink

# SQLite database URL
engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})

# Vegetable data with nutrition tags
vegetables_data = [
    {
        "name": "가지",
        "category": "채소",
        "nutrition_tags": ["안토시아닌", "식이섬유", "칼륨"],
    },
    {
        "name": "감자",
        "category": "구황작물",
        "nutrition_tags": ["칼륨", "비타민C", "비타민B6"],
    },
    {
        "name": "고구마",
        "category": "구황작물",
        "nutrition_tags": ["베타카로틴", "비타민C", "칼륨"],
    },
    {
        "name": "단호박",
        "category": "채소",
        "nutrition_tags": ["베타카로틴", "비타민A", "칼륨"],
    },
    {
        "name": "당근",
        "category": "채소",
        "nutrition_tags": ["베타카로틴", "비타민K", "항산화"],
    },
    {
        "name": "대파",
        "category": "채소",
        "nutrition_tags": ["비타민C", "칼슘"],
    },
    {
        "name": "무",
        "category": "채소",
        "nutrition_tags": ["비타민C", "칼륨", "식이섬유"],
        "color_theme": "WHITE"
    },
    {
        "name": "밤",
        "category": "구황작물",
        "nutrition_tags": ["비타민B6", "마그네슘", "식이섬유"],
    },
    {
        "name": "브로콜리",
        "category": "채소",
        "nutrition_tags": ["비타민C", "비타민K", "항산화"],
    },
    {
        "name": "시금치",
        "category": "채소",
        "nutrition_tags": ["철분", "엽산", "비타민K"],
    },
    {
        "name": "아스파라거스",
        "category": "채소",
        "nutrition_tags": ["엽산", "비타민K", "항산화"],
    },
    {
        "name": "양배추",
        "category": "채소",
        "nutrition_tags": ["비타민K", "비타민C"],
    },
    {
        "name": "양파",
        "category": "채소",
        "nutrition_tags": ["퀘르세틴", "비타민C", "황화합물"],
    },
    {
        "name": "연근",
        "category": "채소",
        "nutrition_tags": ["비타민C", "철분", "식이섬유"],
    },
    {
        "name": "옥수수",
        "category": "구황작물",
        "nutrition_tags": ["식이섬유", "비타민B1", "항산화"],
    },
    {
        "name": "청경채",
        "category": "채소",
        "nutrition_tags": ["비타민A", "칼슘", "항산화"],
    },
    {
        "name": "콩나물",
        "category": "채소",
        "nutrition_tags": ["비타민C", "엽산", "단백질"],
        "color_theme": "WHITE"
    },
    {
        "name": "토마토",
        "category": "채소",
        "nutrition_tags": ["라이코펜", "비타민C", "칼륨"],
    },
    {
        "name": "팽이",
        "category": "버섯",
        "nutrition_tags": ["나이아신", "리신", "항산화"],
        "color_theme": "WHITE"
    },
    {
        "name": "표고",
        "category": "버섯",
        "nutrition_tags": ["비타민D", "셀레늄", "식이섬유"],
    },
]

# Nutrition tags description
nutrition_tags_info = {
    "비타민A": "시력과 면역기능에 도움을 주는 영양소",
    "비타민B1": "탄수화물 대사와 에너지 생성에 필요한 영양소",
    "비타민B6": "단백질과 아미노산 대사에 필요한 영양소",  # 추가
    "비타민C": "항산화 작용과 면역력 강화에 도움을 주는 영양소",
    "비타민D": "칼슘 흡수를 돕고 뼈 건강에 중요한 영양소",
    "비타민K": "혈액응고와 뼈 건강에 중요한 영양소",
    "철분": "적혈구 생성에 필요한 영양소",
    "칼슘": "뼈와 치아 형성에 필요한 영양소",
    "칼륨": "혈압 조절과 근육 기능에 도움을 주는 영양소",
    "식이섬유": "장 건강과 변비 예방에 도움을 주는 영양소",
    "단백질": "근육과 조직 형성에 필요한 영양소",
    "탄수화물": "에너지원으로 사용되는 주요 영양소",
    "엽산": "세포 분열과 성장에 필요한 영양소",
    "아연": "면역기능과 상처치유에 도움을 주는 영양소",
    "베타카로틴": "비타민A의 전구체이며 항산화 작용을 하는 영양소",
    "퀘르세틴": "항산화, 항염증 작용을 하는 플라보노이드",
    "황화합물": "항균, 항산화 작용을 하는 화합물",
    "안토시아닌": "항산화, 항염증 작용을 하는 식물성 색소",  # 추가
    "셀레늄": "항산화 작용과 면역기능 강화에 도움을 주는 미네랄",  # 추가
    "나이아신": "에너지 대사와 신경계 기능에 필요한 비타민 B3",  # 추가
    "리신": "단백질 합성과 성장에 필요한 필수 아미노산",  # 추가
    "마그네슘": "근육과 신경 기능, 뼈 건강에 필요한 미네랄",  # 추가
    "항산화": "세포 손상을 막고 노화를 늦추는데 도움을 주는 물질",  # 추가
    "라이코펜": "항산화 작용을 하는 카로티노이드 계열의 색소"  # 추가 (리코펜의 한글 표기)
}


def seed_database():
    with Session(engine) as session:
        # Create categories first
        # unique_categories = set(veg["category"] for veg in vegetables_data)
        category_map = {}  # To store category id mapping

        for category_name in ["채소", "버섯", "구황작물"]:
            category = Category(
                name=category_name, description=f"{category_name} 종류의 채소들"
            )
            session.add(category)
            session.commit()
            session.refresh(category)
            category_map[category_name] = category.id

        # Create nutrition tags
        nutrition_tag_map = {}
        for tag_name, description in nutrition_tags_info.items():
            tag = NutritionTag(name=tag_name, description=description)
            session.add(tag)
            session.commit()
            session.refresh(tag)
            nutrition_tag_map[tag_name] = tag.id

        # Create ingredients with their nutrition tags
        for veg in vegetables_data:
            # Create ingredient
            ingredient = Ingredient(
                name=veg["name"], category_id=category_map[veg["category"]],
                color_theme=ColorTheme.BLACK if veg.get("color_theme") != "WHITE" else ColorTheme.WHITE
            )
            session.add(ingredient)
            session.commit()
            session.refresh(ingredient)

            # Add nutrition tags (maximum 3)
            for tag_name in veg["nutrition_tags"][:3]:  # Limit to first 3 tags
                link = IngredientNutritionLink(
                    ingredient_id=ingredient.id,
                    nutrition_tag_id=nutrition_tag_map[tag_name],
                )
                session.add(link)

        session.commit()


if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully!")
