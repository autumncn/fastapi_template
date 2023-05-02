import datetime
import os
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")
# templates.env.globals["NOW_YEAR"] = datetime.date.today().year
# templates.env.add_extension("jinja2.ext.i18n")