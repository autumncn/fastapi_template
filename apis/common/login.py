import datetime
import json
from typing import Optional

import captcha
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, APIRouter, Response, Request, status, HTTPException, Form
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
# from fastapi.responses import RedirectResponse

from db.crud.login import authenticate_user
from db.crud.userLoginLogs import create_userLoginLog
from db.crud.users import get_user_by_email, create_user, modify_user, update_user_login, update_user_lang
from db.database import get_db
from core.security import create_access_token
from core.config import settings
from db.schemas.tokens import Token
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer

from db.schemas.userLoginLogs import UserLoginLogCreate
from db.schemas.users import UserCreate, UserModify, UpdateUserLogin, UpdateUserLang
from dependencies import templates
from service.ipService import read_ip_detail
from service.menuService import get_menu_list_by_user_permission, get_menu_path_by_user_permission
from utils.CaptchaUtil import gen_captcha_text_and_image
from utils.CyptoUtil import get_uuid
from utils.JsonUtil import obj_as_dict, obj_as_json
from libs.fastapi_babel import _
from logs.logger import logger

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")  #new

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    # print(f'cookies (req): {request.cookies}')
    # print(f'headers: {request.headers}')
    # print(f'tokens: {request.cookies.token}')
    response_to_login = templates.TemplateResponse("view/login.html", {"request": request})
    response_to_dashboad = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    cookies = request.cookies
    if 'token' not in cookies:
        return response_to_login
    user_token = cookies.get('token')
    get_user = await request.app.state.redis.get(user_token)
    if get_user is None:
        await request.app.state.redis.delete(user_token)
        return response_to_login
    return response_to_dashboad

@router.get('/captcha')
def get_captcha(request: Request):
    # img, text = img_captcha()
    text, img = gen_captcha_text_and_image(save=False)
    uuid = str(get_uuid())
    captcha['img'] = img
    captcha['uuid'] = uuid
    request.app.state.redis.set(text, uuid, timedelta(minutes=5))
    return captcha

@router.post("/login", response_class=HTMLResponse)
async def login_for_access_token(request: Request,
                                 form_data: OAuth2PasswordRequestForm = Depends(),
                                 remember: str = Form(None),
                                 db: Session= Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password,db)
    # print(remember)
    # user username in the form as email
    if not user:
        request.session["error"] = _("incorrect_username_or_password")
        return templates.TemplateResponse(
                "view/login.html",
                status_code=status.HTTP_401_UNAUTHORIZED,
                context={"request": request}
        )
    if (user.is_active != 1):
        # return resp_401(msg="User is not exist")
        return templates.TemplateResponse(
                "view/login.html",
                status_code=status.HTTP_401_UNAUTHORIZED,
                context={"request": request, "error": _("user_is_not_exist")},
            )

    user_allow_menu_path = get_menu_path_by_user_permission(user_login_email=user.email, db=next(get_db()))
    await request.app.state.redis.set(user.email + '_user_allow_menu_path', json.dumps(user_allow_menu_path))
    menu_items = get_menu_list_by_user_permission(user_login_email=user.email, skip=0, limit=100, db=next(get_db()))
    await request.app.state.redis.set(user.email + '_menu_items', json.dumps(menu_items))

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    await request.app.state.redis.set(access_token, obj_as_json(user), access_token_expires)
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
    response.set_cookie('token', access_token)
    # print("user language is ",user.language)
    if user.language:
        response.set_cookie("language", user.language)
    # else:
    #     response.set_cookie("language", "en")
    if remember == "on":
        expire = 3600 * 24 * 30
        response.set_cookie("remember", "on", max_age=expire)
        response.set_cookie("login", user.email, max_age=expire)
    else:
        response.delete_cookie("remember")


    new_user = UpdateUserLogin(
        id=user.id,
        email=user.email,
        date_entered=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    update_user_login(db, new_user)

    try:
        get_ip_detail = read_ip_detail(request.client.host)
        login_from = get_ip_detail['result']['areacode']
        if login_from is None:
            login_from = "-"
        # print("login_from:", login_from)
        new_user_login_log = UserLoginLogCreate(
            user_id=user.id,
            ip=request.client.host,
            login_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            country_code=login_from,
            ua=request.headers.get('user-agent')
        )
        # print("new_user_login_log:", new_user_login_log)
        create_userLoginLog(db, new_user_login_log)
    except Exception as e:
        # print("Error:", e)
        logger.error(e)

    return response


#new function, It works as a dependency
async def get_current_user_from_token(token: str = Depends(oauth2_scheme),db: Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        # print("username/email extracted is ",username)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(email=username,db=db)
    if user is None:
        raise credentials_exception
    return user

@router.post('/logout')
async def logout(request: Request, response: Response):
    # print(f'cookies (req): {request.cookies}')
    # print(f'headers: {request.headers}')
    # return {'message': 'Logout Success!'}
    cookies = request.cookies
    print(cookies)
    if 'token' in cookies:
        user_token = cookies.get('token')
        print('delete token: ', user_token)
        await request.app.state.redis.delete(user_token)
    response = RedirectResponse('/login', status_code=status.HTTP_302_FOUND)
    response.delete_cookie('token')
    # for cookie in request.cookies:
    #     response.delete_cookie(cookie)
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    # print(f'cookies (req): {request.cookies}')
    # print(f'headers: {request.headers}')
    # print(f'tokens: {request.cookies.token}')
    response = templates.TemplateResponse("view/registration.html", {"request": request})
    response.delete_cookie('login')

    cookies = request.cookies
    if 'token' not in cookies:
        return response
    user_token = cookies.get('token')
    get_user = await request.app.state.redis.get(user_token)
    if get_user is None:
        await request.app.state.redis.delete(user_token)
    return response

@router.post("/register", response_class=HTMLResponse)
async def register_with_email(request: Request,response: Response,
                                 email: str = Form(None),
                                 password: str = Form(None),
                                 re_password: str = Form(None),
                                 db: Session= Depends(get_db),
                                 ):
    return templates.TemplateResponse(
        "view/registration.html",
        status_code=status.HTTP_401_UNAUTHORIZED,
        context={"request": request, "error": _("register_is_not_allowed")},
    )

@router.get("/forget_password", response_class=HTMLResponse)
async def forget_password_page(request: Request, db: Session = Depends(get_db)):
    get_login_user_email = request.cookies.get("login")

    user = get_user_by_email(email=get_login_user_email, db=db)

    return templates.TemplateResponse("view/forget_password.html", {"request": request, "user": user})


@router.get("/profile")
async def read_profile_by_login(request: Request, db: Session = Depends(get_db)):
    get_login_user_email = request.cookies.get("login")

    user = get_user_by_email(email=get_login_user_email, db=db)

    return templates.TemplateResponse("view/profile.html", {"request": request, "user": user})

@router.post("/profile")
async def set_profile_by_login(
        request: Request,
        set_email: Optional[str] = Form(None),
        set_lang: Optional[str] = Form(None),
        db: Session = Depends(get_db)):
    get_login_user_email = request.cookies.get("login")
    user = get_user_by_email(email=get_login_user_email, db=db)
    print(set_email, set_lang)
    redirect_response = RedirectResponse("/profile", status_code=status.HTTP_302_FOUND)

    if set_email is None:
        set_email = user.email
    if set_lang is None:
        set_lang = user.language
    else:
        redirect_response.set_cookie("language", set_lang, max_age=3600 * 24 * 30)

    new_user = UpdateUserLang(
        id=user.id,
        language=set_lang,
        modify_by=user.email,
        modify_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    update_user_lang(db=db, user=new_user)
    return redirect_response
