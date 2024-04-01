import os.path
import re
import sys

import yaml
import json
from potencent.lib.CommonUtils import img2base64
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ocr.v20181119 import ocr_client, models

from main import Logger


class ReadRes:

    def __init__(self, errorMsg='', isSuccess: bool = True, Text: str = ''):
        self.errorMsg = errorMsg
        self.isSuccess = isSuccess
        self.Text = ''


class ReadPic:

    def __init__(self):
        self.configPath = os.path.join(sys.path[0], 'potentcent-config.toml')
        self.is_success = True  # 判断是否识别正常
        self.message = ''  # 异常信息
        self.text_info = ''  # 识别正常文本
        with open('userinfo.yml') as f:
            self.userInfo = yaml.safe_load(f)

    def __read_image(self, image):
        Logger.info(f'识别图片：{image}')
        cred = credential.Credential(secret_id=self.userInfo['SecretId'], secret_key=self.userInfo['SecretKey'])
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "ocr.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = ocr_client.OcrClient(cred, "ap-beijing", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.GeneralBasicOCRRequest()
        params = {
            "ImageBase64": img2base64(image),
            "ImageUrl": None,
            "Scene": None,
            "LanguageType": "zh_rare",
            "IsPdf": True,
            "PdfPageNumber": 1,
            "IsWords": None
        }
        params.update({'ImageBase64': img2base64(image)})
        req.from_json_string(json.dumps(params))
        # 返回的resp是一个GeneralBasicOCRResponse的实例，与请求对象对应
        from tencentcloud.common.exception import TencentCloudSDKException
        try:
            resp = client.GeneralBasicOCR(req)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException) and e.requestId:
                return ReadRes(isSuccess=False, errorMsg=e.message)
            else:
                return ReadRes(isSuccess=False, errorMsg='图片上传失败，请检查网络')
        return resp.TextDetections

    def read_pic_name(self, pic_file: str, only_name: bool = False, row: int = 0, ):
        name = ''
        if not os.path.exists(pic_file):
            return name
        if row <= 0:
            text = self.__read_image(pic_file)
            if isinstance(text, list):
                n = len(text) - 1
                i = 0
                while i < n:
                    name_key = str(text[i].DetectedText).strip()
                    if not only_name:
                        if name_key == '产品':
                            only_name = True
                            product_item = text[i].ItemPolygon
                            if text[i + 1].ItemPolygon.X > product_item.X:
                                name += text[i + 1].DetectedText
                            elif text[i - 1].ItemPolygon.X > product_item.X:
                                name += text[i - 1].DetectedText
                            i += 1
                        elif name_key.startswith('产品'):
                            only_name = True
                            name += name_key.split('产品')[-1]
                        i += 1
                        continue
                    else:
                        if name_key == '名称':
                            name_item = text[i].ItemPolygon
                            if text[i + 1].ItemPolygon.X > name_item.X:
                                name += text[i + 1].DetectedText
                            elif text[i - 1].ItemPolygon.X > name_item.X:
                                name += text[i - 1].DetectedText
                            break
                        elif name_key.startswith('名称'):
                            name += name_key.split('名称')[-1]
                            break
                        i += 1
            else:
                return text  # 返回异常
        else:
            text = self.__read_image(pic_file)
            if len(text) >= row - 1:
                name = text[row - 1].DetectedText
        name = re.sub('[\\\\/":|*?<> ]', '', name)
        return name
