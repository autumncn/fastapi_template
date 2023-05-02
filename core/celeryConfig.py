# -*- coding: utf-8 -*-
from kombu import Queue

from celery import Celery

from core.config import settings

celery_app = Celery("tasks",
                    broker='redis://127.0.0.1:49999/0',
                    backend='redis://127.0.0.1:49999/0'
                    )

celery_app.conf.update(
    # broker_url=settings.REDIS_URI,
    # result_backend=settings.REDIS_URI,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    redis_max_connections=1000,  # 增加最大连接数
    broker_heartbeat=10,  # 减少心跳时间
    broker_pool_limit=100,  # 增加连接池大小
    task_queues=(
        Queue("default", routing_key="task.#"),
    ),
    task_default_queue="default",
    task_default_exchange="tasks",
    task_default_exchange_type="topic",
    task_default_routing_key="task.default",
    worker_concurrency=4,
    # task_ignore_result=True,
    task_track_started=True,
    task_acks_late=True,
)

celery_app.conf.imports = [
    'apis.api'
]

'''
#celery -A core.celeryConfig.celery_app worker --loglevel=info
#不允许并发 一次请求一个stable diffusion
celery -A core.celeryConfig.celery_app worker -c 1 --loglevel=info
celery -A core.celeryConfig.celery_app flower --port=5555


nano /lib/systemd/system/celery.service

[Unit]
Description=celery 2023-03-27
After=network.target

[Service]
WorkingDirectory=/usr/local/applications/pythonProj/cn_server
ExecStart=/root/miniconda3/envs/py3106/bin/celery core.celeryConfig.celery_app worker --loglevel=info
StandardOutput=file:/usr/local/applications/pythonProj/cn_server/celery.log
#TimeoutSec=0
#StandardOutput=tty
RemainAfterExit=yes
#SysVStartPriority=88

[Install]
WantedBy=multi-user.target

'''
