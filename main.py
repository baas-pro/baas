import logging
import multiprocessing
import os
import threading
from flask import Flask
from common import process, app
from web.baas import baas
from web.configs import configs


def run_flask():
    f = Flask(__name__, static_folder='web/static', static_url_path='/static')
    f.register_blueprint(baas)
    f.register_blueprint(configs)
    f.run(debug=False, port=1117)


if __name__ == '__main__':
    main_process_pid = os.getpid()
    multiprocessing.freeze_support()

    process.manager = multiprocessing.Manager()
    process.processes_task = process.manager.dict()

    if os.getpid() == main_process_pid:
        flask_thread = threading.Thread(target=run_flask)
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        flask_thread.daemon = True
        flask_thread.start()
        app.start()
