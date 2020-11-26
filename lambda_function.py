import json
import os
from botocore.vendored import requests
import base64


def check_param(event:dict, param:str, field_errors:dict)->str:
    # checks for key and if val is null or an empty string
    if param in event and event[param] and str(event[param]).strip():
        return str(event[param])
    else:
        field_errors[param] = "Required"
        return None
        
        
def lambda_handler(event, context):
    field_errors = {}
    name = check_param(event, 'name', field_errors)
    email = check_param(event, 'email', field_errors)
    message = check_param(event, 'message', field_errors)
    phone = check_param(event, 'phone', field_errors) 
 
    if field_errors: 
        raise Exception(json.dumps({'field_errors': field_errors}))
    
    telegram_msg = f'From: {name}\nEmail: {email}\nMessage {message}\nPhone: {phone}'

    form_chat_id = os.environ['FORM_GROUP_ID']
    test_chat_id = os.environ['test']
    cv_form_chat_id = os.environ['CV_FORM_GROUP_ID']
    telegram_token = os.environ['TELEGRAM_BOT_API_KEY']
    
    api_url = f"https://api.telegram.org/bot{telegram_token}/"

    try:
        if event['debug']:
            chat_id = test_chat_id
        else:
            chat_id = form_chat_id
    except Exception as e:
        chat_id = form_chat_id

    
    try: 
        if event['filename'] :
            try:
                if event['debug']:
                    chat_id = test_chat_id
                else:
                    chat_id = cv_form_chat_id
            except Exception as e:
                chat_id = cv_form_chat_id
            
            # file_content = base64.b64decode(event['filedata'])
            file_content = event['filedata'].encode("utf-8")
            file_path = "/tmp/"+event['filename']
            with open(file_path,"wb") as f:
                # f.write(file_content.decode("utf-8"))
                f.write(base64.decodebytes(file_content))
            
            with open(file_path, "rb") as file:   
                files = {"document":file}
                # params = {'chat_id': chat_id, 'text': telegram_msg, 'caption': event['filename']}
                params = {'chat_id': chat_id, 'caption': telegram_msg}
                # res = requests.post(api_url + "sendDocument", data=datares).json()
                res = requests.post(api_url + "sendDocument", data=params, files=files).json()
            
    except Exception as e:
        # params = {'chat_id': test_chat_id, 'text': f'Oooops... Some error.. \n {telegram_msg} + \n\n {e}' }
        params = {'chat_id': chat_id, 'text': telegram_msg}
        res = requests.post(api_url + "sendMessage", data=params).json()
        
    
    if res["ok"]:
        return {
            'statusCode': 200,
            'body': "Send",
        }
    else:
        print(res)
        return {
            'statusCode': 400,
            'body': res
        }
