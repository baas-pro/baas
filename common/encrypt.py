import hashlib


def md5(s):
    """
    对给定的字符串s执行MD5哈希加密。
    @param s: 要加密的字符串
    @return: 加密后的32位十六进制字符串
    """
    hm = hashlib.md5()
    hm.update(s.encode('utf-8'))  # 确保传入的字符串被编码为字节
    return hm.hexdigest()
