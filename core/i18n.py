from fastapi import Request
from libs.fastapi_babel import Babel, BabelConfigs, _
from core.config import settings
from dependencies import templates
from logs.logger import logger
DEFAULT_LANGUAGE = "en"
# SUPPORTED_LANGUAGE = ["ja", "fa", "en", "zh ", "ko"]
SUPPORTED_LANGUAGE = ["en", "zh"]

async def get_lang(request: Request):
    lang = request.headers.get("Accept-Language", DEFAULT_LANGUAGE)
    lang = lang[:2]
    lang = DEFAULT_LANGUAGE if lang not in SUPPORTED_LANGUAGE else lang
    return lang


async def check_trans(babel: Babel):
    print(babel.locale)
    print(babel.config.ROOT_DIR)
    print(babel.config.BABEL_TRANSLATION_DIRECTORY)
    # langs = ['en', 'fa', 'ja', 'zh', 'ko']
    langs = ['en', 'zh']
    msg = _("token_expired_please_relogin_401")
    logger.info(f'{babel.locale} - {msg}')
    print(f'{babel.locale} - {msg}')

    for lang in langs:
        # babel.locale = "en"
        babel.locale = lang
        msg = _("return_home")
        logger.info(f'{lang} - {msg}')
        print(f'{lang} - {msg}')

configs = BabelConfigs(
    # ROOT_DIR=__file__,
    ROOT_DIR=settings.BASE_DIR,
    BABEL_DEFAULT_LOCALE="en_UK",
    BABEL_TRANSLATION_DIRECTORY="locales",
)
#
babel = Babel(
    configs=configs
)
#
babel.install_jinja(templates)

if __name__ == "__main__":
    # babel.run_cli()
    check_trans(babel)


'''

第一次
pybabel extract -F babel.cfg -o messages.pot .
pybabel init -i messages.pot -d locales -l zh
pybabel init -i messages.pot -d locales -l en
后面更新
pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d locales

生成翻译文件
#pybabel compile -d locales
pybabel compile -d locales -D messages




'''