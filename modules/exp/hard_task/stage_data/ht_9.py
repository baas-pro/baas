stage_data = {
    '9-1': {
        'start': {
            '1': (490, 300),
            '2': (575, 575)
        },
        'action': [
            # 第一回合
            {'t': 'click', 'p': (688, 275), 'ec': True, 'desc': "1 right"},
            {'t': 'click', 'p': (690, 415), 'wo': True, 'desc': "2 upper right"},

            # 第二回合
            {'t': 'exchange', 'ec': True, 'desc': "change to 2"},
            {'t': 'click', 'p': (740, 350), 'ec': True, 'desc': "2 upper right"},
            {'t': 'click', 'p': (745, 355), 'desc': "choose 2"},
            {'t': 'click', 'p': (635, 345), 'desc': "change"},
            {'t': 'click', 'p': (860, 350), 'wo': True, 'desc': "1 right"},

            # 第三回合
            {'t': 'exchange', 'ec': True, 'desc': "change to 2"},
            {'t': 'click', 'p': (405, 320), 'wo': True, 'desc': "2 left & get box"},
            {'t': 'click', 'p': (900, 420), 'desc': "1 left"},
        ]
    },
    '9-1-box': '9-1',
    '9-1-task': '9-1',
    '9-2': {
        'start': {
            '1': (435, 220),
            '2': (525, 685)
        },
        'action': [
            # 第一回合
            {'t': 'click', 'p': (675, 355), 'ec': True, 'desc': "1 lower right"},
            {'t': 'click', 'p': (685, 425), 'wo': True, 'desc': "2 upper right"},

            # 第二回合
            {'t': 'exchange', 'ec': True, 'desc': "change to 2"},
            {'t': 'click', 'p': (740, 360), 'ec': True, 'desc': "2 upper right"},
            {'t': 'click', 'p': (800, 270), 'wo': True, 'desc': "1 right"},

            # 第三回合
            {'t': 'click', 'p': (800, 225), 'ec': True, 'desc': "1 upper right"},
            {'t': 'click', 'p': (720, 465), 'wo': True, 'desc': "2 right"},

            # 第四回合
            {'t': 'exchange', 'ec': True, 'desc': "change to 2"},
            {'t': 'click', 'p': (785, 550), 'wo': True, 'desc': "2 lower right & get box"},
            {'t': 'click', 'p': (720, 355), 'desc': "1 right"},
        ]
    },
    '9-2-box': '9-2',
    '9-2-task': {
        'start': {
            '1': (435, 220)
        },
        'action': [
            # 第一回合
            {'t': 'click', 'p': (585, 385), 'wo': True, 'desc': "1 lower right"},

            # 第二回合
            {'t': 'click', 'p': (705, 380), 'wo': True, 'desc': "1 right"},

            # 第三回合
            {'t': 'click', 'p': (845, 285), 'desc': "1 right"},
        ]
    },
    '9-3': {
        'start': {
            '1': (760, 470),
            '2': (730, 280)
        },
        'action': [
            # 第一回合
            {'t': 'exchange', 'ec': True, 'desc': "change to 2"},
            {'t': 'click', 'p': (585, 430), 'ec': True, 'desc': "2 lower left"},
            {'t': 'click', 'p': (580, 420), 'desc': "choose 2"},
            {'t': 'click', 'p': (480, 420), 'desc': "change"},
            {'t': 'click', 'p': (460, 420), 'wo': True, 'desc': "1 left"},

            # 第二回合
            {'t': 'click', 'p': (435, 500), 'ec': True, 'desc': "1 lower left"},
            {'t': 'click', 'p': (870, 465), 'wo': True, 'desc': "2 right"},

            # 第三回合
            {'t': 'exchange', 'ec': True, 'desc': "change to 2"},
            {'t': 'click', 'p': (840, 295), 'wo': True, 'desc': "2 upper right & get box"},
            {'t': 'click', 'p': (375, 400), 'desc': "1 left"},

        ]
    },
    '9-3-box': '9-3',
    '9-3-task': '9-3',
}
