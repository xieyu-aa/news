from qiniu import Auth, put_data

#需要填写你的 Access Key 和 Secret Key
access_key = 'QdYihoHdNftdfFtSdMr7ezeJb781HIh_FR-vxFdU'
secret_key = 'nLqJN9N3YR2NEx-Ngev3XMERt696ttpqA7SeM0lZ'

def image_url(image_data):
    #构建鉴权对象
    q = Auth(access_key, secret_key)

    #要上传的空间
    bucket_name = 'new3333'

    #上传后保存的文件名
    key = None

    # 处理上传结果
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_data(token, key, image_data)
    print(ret)
    print(info)
    if info.status_code == 200:
        return ret.get('key')
    else:
        return None
if __name__ == '__main__':
    with open('./滑稽.jpg', 'rb') as f:
        image_data = f.read()
        image_url(image_data)





