from __future__ import annotations

import inspect
import json
import logging
import os
from datetime import datetime
from logging import Formatter, Handler, getLogger, handlers
from pathlib import Path
from urllib.request import Request, urlopen

from rich.logging import RichHandler
class Logger:
    """
    ログを管理するためのクラスです。

    Attributes
    ----------
    log_level : str
        ログレベル ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')。デフォルトは 'INFO'。
    save_log_dir : str
        ログファイルを保存するディレクトリのパス。デフォルトは 'logs'。

    Methods
    -------
    debug(msg: str) -> None
        DEBUG レベルのログを出力します。
    info(msg: str) -> None
        INFO レベルのログを出力します。
    warn(msg: str) -> None
        WARNING レベルのログを出力します。
    error(msg: str, exc_info: bool = True) -> None
        ERROR レベルのログを出力します。exc_info が True の場合、例外情報も表示します。
    critical(msg: str) -> None
        CRITICAL レベルのログを出力します。
    webhook_info(msg: str, embed: dict) -> None
        webhook : INFO レベルのログを送信します。
    webhook_error
        webhook : ERROR レベルのログを送信します。

    """

    def __init__(self,  *,
                 log_level: str = 'INFO',
                 save_log_dir: str = 'logs'):

        # Logger設定
        self.log_dir: Path = Path(save_log_dir)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        log_file_path: Path = self.log_dir / 'app.log'

        stdout_formatter: Formatter = Formatter(fmt='%(message)s')
        file_formatter: Formatter = Formatter(
            fmt='%(asctime)s.%(msecs)03d %(levelname)7s %(message)s [%(name)s:%(lineno)d]',
            datefmt='%Y/%m/%d %H:%M:%S')

        stdout_handler: Handler = RichHandler(rich_tracebacks=True)
        stdout_handler.setFormatter(fmt=stdout_formatter)
        file_handler: Handler = handlers.TimedRotatingFileHandler(
            filename=log_file_path,
            when='MIDNIGHT',
            interval=1,
            encoding='UTF-8',
            backupCount=0)
        file_handler.setFormatter(fmt=file_formatter)
        file_handler.namer = self.namer

        logging.basicConfig(level=log_level, handlers=[
                            stdout_handler, file_handler])
        caller_func_name: str = inspect.stack()[1].filename.split('/')[-1]
        self.logger = getLogger(name=caller_func_name)

    # アーカイブのファイル名を指定

    def namer(self, name):
        parts = name.rsplit('/', 1)
        date_str = parts[1].split('.')[-1]
        date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y%m%d')
        archive_file_name = f"{parts[0]}/app_{date}.log"
        return archive_file_name

    def debug(self, msg: str) -> None:
        self.logger.debug(msg, stacklevel=2)

    def info(self, msg: str) -> None:
        self.logger.info(msg, stacklevel=2)

    def warn(self, msg: str) -> None:
        self.logger.warning(msg, stacklevel=2)

    def error(self, msg: str, *, exc_info: bool = True) -> None:
        self.logger.error(msg, exc_info=exc_info, stacklevel=2)

    def critical(self, msg: str) -> None:
        self.logger.critical(msg, stacklevel=2)