from sqlmodel import Session, create_engine

from models.common import CookingMethod, CookingTool, HeatingMethod

# SQLite database URL
engine = create_engine(
    "sqlite:///test.db", connect_args={"check_same_thread": False}
)

# Cooking methods data
cooking_methods_data = [
    {
        "name": "데치기",
        "description": "짧은 시간 동안 끓는 물에 넣었다가 건지는 조리법",
        "icon_url": None
    },
    {
        "name": "찌기",
        "description": "수증기로 익히는 조리법",
        "icon_url": None
    },
    {
        "name": "삶기",
        "description": "물에 넣고 완전히 익히는 조리법",
        "icon_url": None
    }
]

# Cooking tools data
cooking_tools_data = [
    {
        "name": "냄비 / 프라이팬",
        "description": "삶기와 데치기에 적합해 빠르고 고르게 익혀요",
        "icon_url": None
    },
    {
        "name": "전자레인지",
        "description": "빠른 조리가 가능하며 간편하게 익혀요",
        "icon_url": None
    },
    {
        "name": "찜통",
        "description": "야채의 식감과 영양소를 보존하며 익혀요",
        "icon_url": None
    }
]

# Heating methods data
heating_methods_data = [
    {
        "name": "인덕션 / 가스레인지",
        "description": "직접 열을 가하는 방식의 가열 방법",
        "icon_url": None
    },
    {
        "name": "전자레인지",
        "description": "전자파를 이용한 가열 방법",
        "icon_url": None
    }
]


def seed_cooking_methods():
    with Session(engine) as session:
        # Add cooking methods
        for method in cooking_methods_data:
            cooking_method = CookingMethod(**method)
            session.add(cooking_method)

        # Add cooking tools
        for tool in cooking_tools_data:
            cooking_tool = CookingTool(**tool)
            session.add(cooking_tool)

        # Add heating methods
        for method in heating_methods_data:
            heating_method = HeatingMethod(**method)
            session.add(heating_method)

        session.commit()


if __name__ == "__main__":
    seed_cooking_methods()
    print("Cooking methods, tools, and heating methods seeded successfully!")
