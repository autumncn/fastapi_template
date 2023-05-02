import json

from fastapi.encoders import jsonable_encoder
from sqlalchemy import inspect


def dict_to_json(dict_input):
    json_output = json.dumps(dict_input, indent=4)
    return json_output


def json_to_dict(json_input):
    output_dict = json.loads(json_input)
    return output_dict

    """ JsonResponse对象转字典 """
def object_to_json(object_input):
    # 使用 dumps函数直接将对象转化为JSON结果
    # ensure_ascii 默认为True，会将汉字转换为ascii码
    # result = json.dumps(object_input,ensure_ascii = False)
    result = jsonable_encoder(object_input)
    return result

def model_list(result):
    list = []
    for row in result:
        dict = {}
        for k,v in row.__dict__.items():
            if not k.startswith('_sa_instance_state'):
                dict[k] = v
        list.append(dict)
    return list

def obj_as_dict(obj):
    """ ORM对象转字典 """
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs} if obj else None

def obj_as_json(obj):
    """ ORM对象转json """
    return json.dumps(obj_as_dict(obj), indent=4)

def list_obj_as_dict(list_obj):
    """ ORM列表对象转字典 """
    return [obj_as_dict(obj) for obj in list_obj]

def jsonResponse_to_json(jsonResponse):
    """ JsonResponse对象转字典 """
    jsonResponse_json = object_to_json(jsonResponse)['body']
    request_body_json = json.loads(jsonResponse_json)
    request_data = request_body_json['data']
    return request_data

def check_list_in_str(check_list, check_str):
    """ 检查列表中的元素是否在字符串中 """
    for i in check_list:
        if i in check_str:
            return True
    return False

if __name__ == '__main__':
    dict_input = {"name": "zhangsan", "age": 18}
    json_output = dict_to_json(dict_input)
    print("字典转json的结果: ", json_output)

    json_input = '{"name": "zhangsan", "age": 18}'
    output_dict = json_to_dict(json_input)
    print("json转字典的结果: ", output_dict)

    object_input = {"name": "zhangsan", "age": 18}
    result = object_to_json(object_input)
    print("对象转json的结果: ", result)


