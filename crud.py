from uuid import uuid4
from sqlalchemy.orm import Session
from models import *
from schemas import *
from auth_handler import *


async def authenticate_user(data: UserAuthSchema, db: Session):
    db_user = await get_user_by_email(db, data.email)
    if db_user is None:
        return False
    if not verify_password(data.password, db_user.hashed_password):
        return False

    token_data = TokenData(
        access_token=db_user.access_token,
        expire_time=db_user.expire_time
    )

    response = UserDBResponse(
        email=db_user.email,
        role=db_user.role,
        token_data=token_data
    )

    return response


async def get_current_user(token: str, db: Session):
    if checkJWT(token):
        user = db.query(User) \
            .join(Token) \
            .filter(Token.access_token == token) \
            .filter(User.id == Token.user_id) \
            .first()
        return user
    else:
        return None


async def get_all_users(db: Session):
    return db.query(User.id,
                    User.email,
                    User.role,
                    Token.access_token,
                    Token.expire_time) \
        .join(Token) \
        .all()


async def get_user_by_email(db: Session, email: str):
    return db.query(User.email,
                    User.hashed_password,
                    User.role,
                    Token.access_token,
                    Token.expire_time) \
        .join(Token) \
        .filter(User.email == email) \
        .first()


async def add_palette(db: Session, palette_data: PaletteSchema, user_id: int):
    db_palette = db.query(Palette).filter(Palette.id == palette_data.id).first()

    if db_palette is None:
        db_palette = Palette(id=palette_data.id)
        db.add(db_palette)

    db_user_palette = db.query(User_Palette) \
        .filter(User_Palette.user_id == user_id) \
        .filter(User_Palette.palette_id == db_palette.id) \
        .first()

    if db_user_palette is None:
        for color in palette_data.colors:
            db_color = db.query(Color).filter(Color.id == color.id).first()

            if db_color is None:
                db_color = Color(id=color.id, name=color.name, hex=color.hex)
                db.add(db_color)

            db_palette_color = Palette_Color(palette_id=palette_data.id, color_id=color.id)
            db.add(db_palette_color)

        db_user_palette = User_Palette(user_id=user_id, palette_id=palette_data.id)
        db.add(db_user_palette)

        db.commit()
        db.expire_all()

    else:
        return {"error": "This palette already in use"}


async def get_palettes(db: Session, user_id: int):
    response = []

    db_palettes = db.query(User_Palette) \
        .filter(User_Palette.user_id == user_id) \
        .all()

    if db_palettes is None:
        return response

    for palette in db_palettes:
        db_colors = db.query(Palette_Color).filter(Palette_Color.palette_id == palette.palette_id).all()
        colors = []

        for color in db_colors:
            db_color = db.query(Color).filter(Color.id == color.color_id).first()
            colors.append(ColorSchema(id=db_color.id, name=db_color.name, hex=db_color.hex))

        response.append(PaletteSchema(id=palette.palette_id, colors=colors))

    return response


async def delete_palette(db: Session, palette_data: PaletteSchema, user_id: int):
    db_user_palette = db.query(User_Palette) \
        .filter(User_Palette.user_id == user_id) \
        .filter(User_Palette.palette_id == palette_data.id) \
        .first()

    if db_user_palette is not None:
        db.delete(db_user_palette)
        db_palettes_colors = db.query(Palette_Color)\
            .filter(Palette_Color.palette_id == palette_data.id)\
            .all()

        for colors in db_palettes_colors:
            db.delete(colors)

        db.commit()
        db.expire_all()
    else:
        return {"error": "This palette does not exist"}


async def get_colors(db: Session, user_id: int):
    db_colors = db.query(Color) \
        .join(User_Color) \
        .filter(User_Color.user_id == user_id) \
        .all()

    return db_colors


async def add_color(db: Session, color_data: ColorSchema, user_id: int):
    db_color = db.query(Color) \
        .filter(Color.id == color_data.id) \
        .first()

    if db_color is None:
        db_color = Color(
            id=color_data.id,
            name=color_data.name,
            hex=color_data.hex
        )
        db.add(db_color)

    db_user_color = db.query(User_Color) \
        .filter(User_Color.user_id == user_id) \
        .filter(User_Color.color_id == db_color.id) \
        .first()

    if db_user_color is None:
        db_user_color = User_Color(user_id=user_id, color_id=color_data.id)

        db.add(db_user_color)
        db.commit()
        db.expire_all()

    else:
        return {"error": "This color already in use"}


async def delete_color(db: Session, color_data: ColorSchema, user_id: str):
    color_for_delete = db.query(User_Color) \
        .filter(User_Color.color_id == color_data.id) \
        .filter(User_Color.user_id == user_id) \
        .first()

    if color_for_delete is not None:
        db.delete(color_for_delete)
        db.commit()
        db.expire_all()
    else:
        return {"error": "This color does not exist"}


async def create_user(db: Session, user_data: UserDBCreateRequest):
    user_id = uuid4().hex

    db_user = User(
        id=user_id,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    db_access_token = Token(
        access_token=user_data.token_data.access_token,
        expire_time=user_data.token_data.expire_time,
        user_id=user_id
    )

    db.add(db_user)
    db.add(db_access_token)

    db.commit()

    db.refresh(db_user)
    db.refresh(db_access_token)

    return db_user
