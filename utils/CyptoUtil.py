from Crypto.Cipher import DES, AES
import binascii
import base64
import os
from Crypto import Random
import uuid

KEY_LENGTH = 8
shared = { 75, 38, 122, 25, 36, 17, 21, 19 }

'''
pip install pycryptodome
'''
class aescrypt():
    def __init__(self,key,model='CBC',iv='1234567812345678',encode_='utf-8'):
        # ['utf-8','gbk']
        self.encode_ = encode_
        self.model =  {'ECB':AES.MODE_ECB,'CBC':AES.MODE_CBC}[model]
        self.key = self.add_16(key)
        self.iv = binascii.hexlify(os.urandom(8))  # even used without binascii.hexlify)
        # print(len(self.iv))

        self.aes = AES.new(self.key, self.model, self.iv)  # 创建一个aes对象
        if model == 'ECB':
            self.aes = AES.new(self.key,self.model) #创建一个aes对象
        # elif model == 'CBC':
            # self.aes = AES.new(self.key,self.model,iv) #创建一个aes对象

        #这里的密钥长度必须是16、24或32，目前16位的就够用了

    async def add_16(self,par):
        par = par.encode(self.encode_)
        while len(par) % 16 != 0:
            par += b'\x00'
        return par

    async def encrypt(self,text):
        text = self.add_16(text)
        try:
            self.encrypt_text = self.aes.encrypt(text)
            return base64.encodebytes(self.encrypt_text).decode().strip()
        except Exception as e:
            print(e)
            return ''

    async def decrypt(self,text):
        text = base64.decodebytes(text.encode(self.encode_))
        try:
            self.decrypt_text = self.aes.decrypt(text)
            return self.decrypt_text.decode(self.encode_).strip('\0')
        except Exception as e:
            print(e)
            return ''

class mycrypt():
    def __init__(self,key,model,iv,encode_):
        # ['utf-8','gbk']
        self.encode_ = encode_
        self.model = {'ECB': AES.MODE_ECB, 'CBC': AES.MODE_CBC}[model]
        key_size = 256
        ulen = int(key_size / 8 / 4 * 3)
        self.key = base64.b64encode(os.urandom(ulen))
        # self.key = self.add_16(key)
        # self.iv = binascii.hexlify(os.urandom(8))  # even used without binascii.hexlify)

    async def add_16(self,par):
        par = par.encode(self.encode_)
        while len(par) % 16 != 0:
            par += b'\x00'
        return par

    async def encrypt(self, data):
        bs = AES.block_size
        self.iv = Random.new().read(bs)
        pad = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        data = cipher.encrypt(pad(data))
        data = self.iv + data
        return (data)

    async def decrypt(self, data):
        bs = AES.block_size
        if len(data) <= bs:
            return (data)
        unpad = lambda s: s[0:-ord(s[-1])]
        self.iv = data[:bs]
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        data = unpad(cipher.decrypt(data[bs:]))
        return (data)

async def get_uuid():
    get_randomnumber_uuid = uuid.uuid4()  # 根据 随机数生成 uuid , 既然是随机就有可能真的遇到相同的，但这就像中奖似的，几率超小，因为是随机而且使用还方便，所以使用这个的还是比较多的。
    return get_randomnumber_uuid

async def get_uuid_md5(namespace,name):
    get_specifiedstr_uuid = uuid.uuid3(namespace,name)  # 里面的namespace和具体的字符串都是我们指定的
    return get_specifiedstr_uuid

async def get_uuid_by_sha1(namespace,name):
    get_specifiedstr_SHA1_uuid = uuid.uuid5(namespace,name)  # 和uuid3()貌似并没有什么不同，写法一样，也是由用户来指定namespace和字符串，不过这里用的散列并不是MD5，而是SHA1.
    return get_specifiedstr_SHA1_uuid
