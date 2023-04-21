from fastapi import FastAPI, HTTPException, Depends, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session
from auth_bearer import JWTBearer
from auth_handler import *
from schemas import *
from database import *
from colorReplace import replace_image_colors
import crud
import json

app = FastAPI()
Base.metadata.create_all(bind=engine)


@app.get("/api/palettes", dependencies=[Depends(JWTBearer())], tags=["Palette"])
async def get_palettes(cred=Depends(JWTBearer()), db=Depends(get_db)):
    user = await crud.get_current_user(cred, db)
    if user is None:
        return {"error": "something wrong"}

    return await crud.get_palettes(db, user.id)


@app.post("/api/palette/add", dependencies=[Depends(JWTBearer())], tags=["Palette"])
async def add_palette(palette_data: PaletteSchema,
                      cred=Depends(JWTBearer()),
                      db=Depends(get_db)):
    user = await crud.get_current_user(cred, db)
    await crud.add_palette(db, palette_data, user.id)
    return {"status": "palette added successfully"}


@app.delete("/api/palette/delete", dependencies=[Depends(JWTBearer())], tags=["Palette"])
async def delete_palette(id: int,
                         cred=Depends(JWTBearer()),
                         db=Depends(get_db)):
    user = await crud.get_current_user(cred, db)
    await crud.delete_palette(db, id, user.id)
    return {"status": "palette deleted successfully"}


@app.post("/api/palette/update", dependencies=[Depends(JWTBearer())], tags=["Palette"])
async def update_palette(id: int,
                         new_palette: PaletteSchema,
                         cred=Depends(JWTBearer()),
                         db=Depends(get_db)):
    user = await crud.get_current_user(cred, db)
    await crud.update_palette(db, palette_id=id, new_palette=new_palette, user_id=user.id)
    return {"status": "palette deleted successfully"}


@app.get("/api/colors", dependencies=[Depends(JWTBearer())], tags=["Color"])
async def get_colors(cred=Depends(JWTBearer()), db=Depends(get_db)):
    user = await crud.get_current_user(cred, db)
    if user is None:
        return {"error": "something wrong"}

    colors = await crud.get_colors(db, user.id)

    return colors


@app.post("/api/color/add", dependencies=[Depends(JWTBearer())], tags=["Color"])
async def add_color(color_data: ColorSchema,
                    cred=Depends(JWTBearer()),
                    db=Depends(get_db)):
    user = await crud.get_current_user(cred, db)
    await crud.add_color(db, color_data, user.id)
    return {"status": "color added successfully"}


@app.delete("/api/color/delete", dependencies=[Depends(JWTBearer())], tags=["Color"])
async def delete_color(id: int,
                       cred=Depends(JWTBearer()),
                       db=Depends(get_db)):
    user = await crud.get_current_user(cred, db)
    await crud.delete_color(db, id, user.id)
    return {"status": "color deleted successfully"}


@app.post("/api/user/signup", tags=["User"])
async def create_user(user_data: UserAuthSchema, db: Session = Depends(get_db)):
    user = await crud.get_user_by_email(db, user_data.email)

    if user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered."
        )

    token = signJWT(user_data.email)
    token_data = TokenData(
        access_token=token['access_token'],
        expire_time=token['expire_time']
    )
    user_request = UserDBCreateRequest(
        email=user_data.email,
        password=user_data.password,
        token_data=token_data
    )

    signedup_user = await crud.create_user(db, user_request)

    return signedup_user


@app.post("/api/user/login", tags=["User"])
async def user_login(user: UserAuthSchema, db: Session = Depends(get_db)):
    response = await crud.authenticate_user(user, db)
    if not response:
        return {"error": "Wrong login details!"}
    else:
        return response


@app.get("/api/user", dependencies=[Depends(JWTBearer())], tags=["User"])
async def get_current_user(db: Session = Depends(get_db), cred=Depends(JWTBearer())):
    db_user = await crud.get_current_user(cred, db)
    db_token = await crud.get_token_info(cred, db)

    return UserDBResponse(
        email=db_user.email,
        role=db_user.role,
        token_data=TokenData(db_token.access_token, db_token.expire_time)
    )


@app.get("/api/users", dependencies=[Depends(JWTBearer())], tags=["User"])
async def get_all_users(db: Session = Depends(get_db)):
    db_users = await crud.get_all_users(db)
    response = []

    for user in db_users:
        response.append(UserDBResponse(
            email=user.email,
            role=user.role,
            token_data=TokenData(user.access_token, user.expire_time)
        ))

    return response


@app.post("/api/colorsReplace", tags=["General"])
async def upload_image_for_replace(file: UploadFile, palette: UploadFile):
    img_bytes = await file.read()
    palette_bytes = await palette.read()

    palette_str = palette_bytes.decode("utf-8")  # Decode the bytes to a string
    palette_dict = json.loads(palette_str)
    print(palette_dict)

    new_image = replace_image_colors(img_bytes, palette_dict['colors'])

    # set the content type header to "image/jpeg" or "image/png", depending on the image format
    headers = {"Content-Type": "image/jpeg"}

    # return the image bytes as the response body
    return Response(content=new_image.getvalue(), headers=headers)
