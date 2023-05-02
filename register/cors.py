# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://suai.cloudtim.com",
    "https://suai.cloudtim.com",
    "http://localhost:8080",
    # "http://0.0.0.0:8080",
]

def register_cors(app: FastAPI):
    """ 跨域请求 """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        # allow_headers=("*", "authentication"),
    )

