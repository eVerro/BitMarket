# -*- coding: UTF-8 -*-
from wallet.models import WithdrawCodes
import hashlib
def checkConfirmCode(user, code):
    """
    Metoda potwierdzająca, czy otrzymany kod zgadza się, z którymś z kodów z niepotwerdzonych użytkowników. 
    """
    hashs = hashlib.md5()
    hashs.update(code)
    code = hashs.hexdigest()
    code = WithdrawCodes.objects.filter(code=code)
    if code is not None:
        code[0].confirm()
    else:
        return False
    return True