import time

from fuzzywuzzy import fuzz

from common import stage, image, config


def screenshot(self):
    self.d.screenshot(config.get_ss_path(self))


def screenshot_get_text(self, area, ocr=None, wait=99999, i=0):
    # 检查文字前，等待加载完成
    stage.wait_loading(self)
    img = self.d.screenshot().crop(area)
    if ocr is None:
        out = self.ocr.ocr(img)
    else:
        out = ocr.ocr(img)
    if len(out) == 0 and wait > 0:
        return screenshot_get_text(self, area, ocr, wait)
    if len(out) == 0:
        return ''
    return out[i]['text']


def screenshot_cut_get_text(self, area, before_wait=0, need_loading=True):
    return self.ocr.ocr(image.screenshot_cut(self, area, before_wait, need_loading))


def screenshot_check_text(self, text, area=(), wait=99999, before_wait=0, need_loading=True, mis_fu=None, mis_argv=None,
                          rate=0.1):
    out = screenshot_cut_get_text(self, area, before_wait, need_loading)
    ex = any(map(lambda d: fuzz.ratio(d.get('text'), text) > 60, out))
    self.logger.info("screenshot_check_text Text:%s Result:%s", text, ex)
    # 如果已经找到 或 不需要等待直接返回结果
    if ex or wait == 0:
        return ex
    time.sleep(self.bc['baas']['base']['ss_rate'])
    if wait < 99999:
        wait -= 1
    if mis_fu is not None:
        mis_fu(*mis_argv)
        time.sleep(rate)
    return screenshot_check_text(self, text, area, wait, before_wait, need_loading, mis_fu, mis_argv, rate)


def screenshot_get_position(self, text, area=(), wait=99999, before_wait=0, need_loading=True):
    out = screenshot_cut_get_text(self, area, before_wait, need_loading)
    for t in out:
        if fuzz.ratio(t.get('text'), text) <= 60:
            continue
        self.logger.info("screenshot_check_text Text:%s Result:%s", text, True)
        return True, t.get('position')
    self.logger.info("screenshot_check_text Text:%s Result:%s", text, False)
    # 不需要等待直接返回结果
    if wait == 0:
        return False, ()
    time.sleep(self.bc['baas']['base']['ss_rate'])
    if wait < 99999:
        wait -= 1
    return screenshot_get_position(self, text, area, wait)
