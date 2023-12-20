from common import image


def close_notice(self):
    """
    关闭通知
    @param self:
    """
    if image.compare_image(self, 'cm_notice', 3):
        self.click(888, 160, False)
