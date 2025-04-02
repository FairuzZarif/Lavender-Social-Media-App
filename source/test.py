import base64
def get_credential():
        ori = "Henry" + ":" + "henry404"
        return base64.b64encode(ori.encode()).decode()


print(get_credential())