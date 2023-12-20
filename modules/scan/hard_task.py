from modules.scan import normal_task

hard_position = {
    1: (1120, 250), 2: (1120, 370), 3: (1120, 480),
}


def start(self):
    normal_task.start(self)
