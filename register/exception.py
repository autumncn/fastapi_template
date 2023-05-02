# -*- coding: utf-8 -*-
import traceback
from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, ProgrammingError, NoResultFound
from sqlalchemy.orm.exc import UnmappedInstanceError
from starlette.requests import Request
from dependencies import templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.error import IpError, ErrorUser, UserNotExist, IdNotExist, SetRedis, AccessTokenFail, PermissionNotEnough, UnicornException
from logs.logger import logger
from libs.fastapi_babel import _


def register_exception(app: FastAPI):
    """ 全局异常捕获 """

    @app.exception_handler(IpError)
    async def ip_error_handler(request: Request, exc: IpError):
        """ ip错误(自定义异常) """
        logger.warning(f"{exc.err_desc}\nURL:{request.method}-{request.url}\nHeaders:{request.headers}")
        # return resp_400(msg=exc.err_desc)
        return resp_400_error_page(request, exc.err_desc)

    @app.exception_handler(ErrorUser)
    async def error_user_handler(request: Request, exc: ErrorUser):
        """ 错误的用户名或密码(自定义异常) """
        logger.warning(f"{exc.err_desc}\nURL:{request.method}-{request.url}\nHeaders:{request.headers}")
        # return resp_400(msg=exc.err_desc)
        return resp_400_error_page(request, exc.err_desc)

    @app.exception_handler(UserNotExist)
    async def user_not_exist_handler(request: Request, exc: UserNotExist):
        """ 用户不存在(自定义异常) """
        logger.warning(f"{exc.err_desc}\nURL:{request.method}-{request.url}\nHeaders:{request.headers}")
        # return resp_400(msg=exc.err_desc)
        # request.session["error"] = _(exc.err_desc)
        return resp_400_error_page(request, exc.err_desc)

    @app.exception_handler(IdNotExist)
    async def id_not_exist_handler(request: Request, exc: IdNotExist):
        """ 查询id不存在(自定义异常) """
        logger.warning(f"{exc.err_desc}\nURL:{request.method}-{request.url}\nHeaders:{request.headers}")
        # return resp_400(msg=exc.err_desc)
        # request.session["error"] = _(exc.err_desc)
        return resp_400_error_page(request, exc.err_desc)

    @app.exception_handler(SetRedis)
    async def set_redis_handler(request: Request, exc: SetRedis):
        """ Redis存储失败(自定义异常) """
        logger.warning(f"{exc.err_desc}\nURL:{request.method}-{request.url}\nHeaders:{request.headers}")
        # return resp_400(msg=exc.err_desc)
        # request.session["error"] = _(exc.err_desc)
        return resp_400_error_page(request, exc.err_desc)

    @app.exception_handler(AccessTokenFail)
    async def access_token_fail_handler(request: Request, exc: AccessTokenFail):
        """ 访问令牌失败(自定义异常) """
        logger.warning(f"{exc.err_desc}\nURL:{request.method}-{request.url}\nHeaders:{request.headers}")
        # return resp_401(msg=exc.err_desc)
        # request.session["error"] = _(exc.err_desc)
        return resp_401_error_page(request, exc.err_desc)

    @app.exception_handler(PermissionNotEnough)
    async def permission_not_enough_handler(request: Request, exc: AccessTokenFail):
        """ 权限不足,拒绝访问(自定义异常) """
        logger.warning(f"{exc.err_desc}\nURL:{request.method}-{request.url}\nHeaders:{request.headers}")
        # return resp_403(msg=exc.err_desc)
        # request.session["error"] = _(exc.err_desc)
        return resp_403_error_page(request, exc.err_desc)

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """ 添加/更新的数据与数据库中数据冲突 """
        text = f"添加/更新的数据与数据库中数据冲突!"
        logger.warning(f"{text}\nURL:{request.method}-{request.url}\nHeaders:{request.headers}\nerror:{exc.orig}")
        # return resp_400(msg=text)
        print(_("update_data_conflict"))
        return resp_400_error_page(request, "update_data_conflict")

    @app.exception_handler(ProgrammingError)
    async def programming_error_handle(request: Request, exc: ProgrammingError):
        """ 请求参数丢失 """
        logger.error(f"请求参数丢失\nURL:{request.method}-{request.url}\nHeaders:{request.headers}\nerror:{exc}")
        # return resp_400(msg='请求参数丢失!(实际请求参数错误)')
        print(_("request_parameter_missing"))
        return resp_400_error_page(request, "request_parameter_missing")

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        """ 请求参数验证异常 """
        logger.error(f"请求参数格式错误\nURL:{request.method}-{request.url}\nHeaders:{request.headers}\nerror:{exc.errors()}")
        # return resp_422(msg=exc.errors())
        # request.session["error"] = _(exc.errors())
        return resp_422_error_page(request, exc.errors())

    @app.exception_handler(ValidationError)
    async def inner_validation_exception_handler(request: Request, exc: ValidationError):
        """ 内部参数验证异常 """
        logger.error(f"内部参数验证错误\nURL:{request.method}-{request.url}\nHeaders:{request.headers}\nerror:{exc.errors()}")
        # return resp_500(msg=exc.errors())
        request.session["error"] = _(exc.errors())
        return resp_500_error_page(request, "500_error_message")


    @app.exception_handler(UnmappedInstanceError)
    async def un_mapped_instance_error_handler(request: Request, exc: UnmappedInstanceError):
        """ 删除数据的id在数据库中不存在 """
        id = request.path_params.get("id")
        text = f"不存在编号为 {id} 的数据, 删除失败!"
        logger.warning(f"{text}\nURL:{request.method}-{request.url}\nHeaders:{request.headers}")
        # return resp_400(msg=text)
        return resp_400_error_page(request, "400_error_message")

    @app.exception_handler(HTTPException)
    async def no_result_found_handler(request: Request, exc: HTTPException):
        return resp_404_error_page(request, "404_error_message")

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        return resp_404_error_page(request, "404_error_message")
        # return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

    #
    # @app.exception_handler(NoResultFound)
    # async def no_result_found_handler(request: Request, exc: NoResultFound):
    #     """ 查询结果为空 """
    #     logger.warning(f"{exc}\nURL:{request.method}-{request.url}\nHeaders:{request.headers}")
    #     # return resp_404(msg="查询结果为空")
    #     return resp_404_error_page(request, "404_error_message")

    @app.exception_handler(UnicornException)
    async def unicorn_exception_handler(request: Request, exc: UnicornException):
        """ 自定义异常 """
        logger.error(f"自定义异常\n{request.method}URL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        # request.session["error"] = _(exc.errors())
        return resp_404_error_page(request, "404_error_message")

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        """ 捕获全局异常 """
        logger.error(f"全局异常\n{request.method}URL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        # return resp_500(msg="服务器内部错误")
        return resp_500_error_page(request, "500_error_message")

def resp_400_error_page(request: Request, error_code_msg: str = "400_error_message"):
    request.session["error_code_msg"] = _(error_code_msg)
    return templates.TemplateResponse(
        "errors/error-400.html", status_code=status.HTTP_400_BAD_REQUEST, context={"request": request}
    )

def resp_401_error_page(request: Request, error_code_msg: str = "401_error_message"):
    request.session["error_code_msg"] = _(error_code_msg)
    return templates.TemplateResponse(
        "errors/error-401.html", status_code=status.HTTP_401_UNAUTHORIZED, context={"request": request}
    )

def resp_403_error_page(request: Request, error_code_msg: str = "403_error_message"):
    request.session["error_code_msg"] = _(error_code_msg)
    return templates.TemplateResponse(
        "errors/error-403.html", status_code=status.HTTP_403_FORBIDDEN, context={"request": request}
    )

def resp_404_error_page(request: Request, error_code_msg: str = "404_error_message"):
    request.session["error_code_msg"] = _(error_code_msg)
    return templates.TemplateResponse(
        "errors/error-404.html", status_code=status.HTTP_404_NOT_FOUND, context={"request": request}
    )

def resp_422_error_page(request: Request, error_code_msg: str = "422_error_message"):
    request.session["error_code_msg"] = _(error_code_msg)
    return templates.TemplateResponse(
        "errors/error-422.html", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, context={"request": request}
    )

def resp_500_error_page(request: Request, error_code_msg: str = "500_error_message"):
    request.session["error_code_msg"] = _(error_code_msg)
    return templates.TemplateResponse(
        "errors/error-500.html",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        context={"request": request},
    )

def resp_502_error_page(request: Request, error_code_msg: str = "502_error_message"):
    request.session["error_code_msg"] = _(error_code_msg)
    return templates.TemplateResponse(
        "errors/error-502.html",
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        context={"request": request},
    )

def resp_503_error_page(request: Request, error_code_msg: str = "503_error_message"):
    request.session["error_code_msg"] = _(error_code_msg)
    return templates.TemplateResponse(
        "errors/error-503.html",
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        context={"request": request},
    )

def resp_504_error_page(request: Request, error_code_msg: str = "504_error_message"):
    request.session["error_code_msg"] = _(error_code_msg)
    return templates.TemplateResponse(
        "errors/error-504.html",
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        context={"request": request},
    )

