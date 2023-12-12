# django-upload-app
Django upload app to use with my JS handle

## Python dependencies
- pip install django
- pip install django-cors-headers

## How to set 
In order for this app to work, you need to set a *profile* first, and on the upload method, *recover it* using the given key/name on the POST request.
DON'T FORGET TO SET STATIC_URL AND TO SET urlpattern TO ACCESS FILES USING THE URL ADDRESS BAR.

```python
Upload.addProfile("client", {
    "url":"http://127.0.0.1:8000/upload/", #server location, which will store the files
     "folder": "./uploads/clients/", #accessible only on backend - folder which the files will be stored
     "types": ["jpeg", "jpg", "png","bmp","svg","webp"], # accepted types for file uploading
      "size": 2621440,  #max file size on upload
      "total": 10 #total amount of files that can be uploaded at once
      })
Upload.addInput("client_picture", "client") #inputName, profile to bind
```

By default, this app uses "uploads" folder on the project to store files

Enjoy!