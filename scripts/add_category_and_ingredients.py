from sqlmodel import Session, create_engine

from models.common import Category, Ingredient, NutritionTag, IngredientNutritionLink

# SQLite database URL
engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})

# Vegetable data with nutrition tags
vegetables_data = [
    {
        "name": "가지",
        "category": "열매채소",
        "nutrition_tags": ["비타민C", "칼륨", "식이섬유"],
    },
    {
        "name": "감자",
        "category": "뿌리채소",
        "nutrition_tags": ["비타민C", "칼륨", "탄수화물"],
    },
    {
        "name": "고구마",
        "category": "뿌리채소",
        "nutrition_tags": ["베타카로틴", "비타민C", "식이섬유"],
    },
    {
        "name": "단호박",
        "category": "열매채소",
        "nutrition_tags": ["베타카로틴", "비타민C", "식이섬유"],
    },
    {
        "name": "당근",
        "category": "뿌리채소",
        "nutrition_tags": ["베타카로틴", "식이섬유", "비타민A"],
    },
    {
        "name": "대파",
        "category": "줄기채소",
        "nutrition_tags": ["비타민A", "비타민C", "황화합물"],
    },
    {
        "name": "무",
        "category": "뿌리채소",
        "nutrition_tags": ["비타민C", "식이섬유", "칼륨"],
    },
    {
        "name": "밤",
        "category": "씨앗채소",
        "nutrition_tags": ["탄수화물", "식이섬유", "비타민B1"],
    },
    {
        "name": "브로콜리",
        "category": "꽃채소",
        "nutrition_tags": ["비타민C", "식이섬유", "칼슘"],
    },
    {
        "name": "시금치",
        "category": "잎채소",
        "nutrition_tags": ["비타민A", "철분", "엽산"],
    },
    {
        "name": "아스파라거스",
        "category": "줄기채소",
        "nutrition_tags": ["엽산", "비타민K", "식이섬유"],
    },
    {
        "name": "양배추",
        "category": "잎채소",
        "nutrition_tags": ["비타민C", "식이섬유", "비타민K"],
    },
    {
        "name": "양파",
        "category": "기타채소",
        "nutrition_tags": ["퀘르세틴", "황화합물", "식이섬유"],
    },
    {
        "name": "연근",
        "category": "기타채소",
        "nutrition_tags": ["식이섬유", "비타민C", "철분"],
    },
    {
        "name": "옥수수",
        "category": "씨앗채소",
        "nutrition_tags": ["식이섬유", "비타민B1", "엽산"],
    },
    {
        "name": "청경채",
        "category": "잎채소",
        "nutrition_tags": ["비타민A", "칼슘", "철분"],
    },
    {
        "name": "콩나물",
        "category": "줄기채소",
        "nutrition_tags": ["비타민C", "엽산", "단백질"],
    },
    {
        "name": "토마토",
        "category": "열매채소",
        "nutrition_tags": ["리코펜", "비타민C", "칼륨"],
    },
    {
        "name": "팽이",
        "category": "버섯",
        "nutrition_tags": ["식이섬유", "비타민D", "단백질"],
    },
    {
        "name": "표고",
        "category": "버섯",
        "nutrition_tags": ["비타민D", "식이섬유", "아연"],
    },
]

# Nutrition tags description
nutrition_tags_info = {
    "비타민A": "시력과 면역기능에 도움을 주는 영양소",
    "비타민B1": "탄수화물 대사와 에너지 생성에 필요한 영양소",
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
    "리코펜": "항산화 작용을 하는 카로티노이드 계열의 영양소",
    "퀘르세틴": "항산화, 항염증 작용을 하는 플라보노이드",
    "황화합물": "항균, 항산화 작용을 하는 화합물",
}


def seed_database():
    with Session(engine) as session:
        # Create categories first
        unique_categories = set(veg["category"] for veg in vegetables_data)
        category_map = {}  # To store category id mapping

        for category_name in unique_categories:
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
                name=veg["name"], category_id=category_map[veg["category"]]
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
