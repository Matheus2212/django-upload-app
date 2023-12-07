import json
from upload.models import Upload
import os
import hashlib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from up.settings import MEDIA_ROOT,MEDIA_URL

# Create your views here.

@csrf_exempt
def UploadGetProfile(request):
    if request.method=='GET':
        print(MEDIA_URL)
        Upload.addProfile("imagem", {"url":"http://127.0.0.1:8000/upload/", "folder": "./uploads/", "types": ["jpeg", "jpg", "png"], "size": 260000, "total": 10})
        Upload.addInput("backend", "imagem")
        Upload.setRootDir("/path/to/root")
        return JsonResponse(Upload.init(),safe=False)
    if request.method == 'POST':
        return_data = {
            'status': False,
            'message': '',
        }
        if 'upload' in request.POST.keys():
            data = json.loads(request.POST['upload'])
            if data:
                if 'profile' not in data or 'name' not in data['profile'] or 'key' not in data['profile'] or (hashlib.md5(data['profile']['name'].encode()).hexdigest() != data['profile']['key']):
                    return_data['status'] = False
                    return_data['message'] = "Error. Upload integrity has been compromised. Upload failed."
                else:
                    profile = Upload.getProfile(data['profile']['name'])
                    if 'fileNameSet' not in data or not data['fileNameSet']:
                        data['fileName'] = Upload.setNewName(data['fileName'])
                    if Upload.saveFile(data['fileName'], data['data'], profile['config']['folder']):
                        return_data['status'] = True
                        return_data['fileName'] = data['fileName']
                        return_data['fileNameSet'] = True
                        return_data['message'] = "File Uploaded"
                        if data["totalRequests"] == (data["currentRequest"] + 1):
                            Upload.unsetLog(data['fileName'], profile['config']['folder'])
                    else:
                        return_data['message'] = "File weren't Uploaded"
            else:
                return_data["message"] = "Error. No data has been received. Upload failed."

        if 'cancel' in request.POST.keys():
            data = json.loads(request.POST['cancel'])
            if data:
                profile = Upload.getProfile(data['profile']['name'])
                path = os.path.join(profile['config']["folder"], data["fileName"])
                Upload.unsetLog(data['fileName'], profile['config']['folder'])
                if Upload.delete(path):
                    return_data["message"] = "Upload canceled."
                    return_data["status"] = True

        if 'delete' in request.POST.keys():
            data = json.loads(request.POST['delete'])
            if data:
                profile = Upload.getProfile(data['profile']['name'])
                path = os.path.join(profile['config']["folder"], data["fileName"])
                if Upload.delete(path):
                    return_data["message"] = "Upload deleted."
                    return_data["status"] = True

        if 'uploadReturn' in locals():
            return_data['profile'] = profile
            return JsonResponse(return_data)

        return JsonResponse(return_data)