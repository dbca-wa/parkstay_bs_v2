import os
import mimetypes
from PIL import Image
from django.conf import settings
from parkstay import models
from django.http import HttpResponse, HttpResponseRedirect

def getFile(request, height, width):
     allow_access = True
     #file_record = models.Campground.objects.get(id=file_id)
     mediafile = request=request.GET.get('mediafile',None) 
     mediafile = mediafile.replace(settings.MEDIA_URL, '')

     local_file = settings.MEDIA_ROOT+'/'+mediafile
     file_name_path = local_file
     extension=mediafile[-3:] 
     if os.path.isfile(file_name_path) is True:
             reszie_file_name = file_name_path[:len(file_name_path)-4]
             reszie_file_name_extension = file_name_path[-4:]
             reszie_fn = reszie_file_name+'-'+height+'x'+width+reszie_file_name_extension
             if os.path.isfile(reszie_fn) is False:
                 img = Image.open(file_name_path)
                 img = img.resize((int(width), int(height)), Image.Resampling.LANCZOS)
                 img.save(reszie_fn)

             the_file = open(reszie_fn, 'rb')
             the_data = the_file.read()
             the_file.close()
             if extension == 'msg':
                 return HttpResponse(the_data, content_type="application/vnd.ms-outlook")
             if extension == 'eml':
                 return HttpResponse(the_data, content_type="application/vnd.ms-outlook")
   
             return HttpResponse(the_data, content_type=mimetypes.types_map['.'+str(extension)])
     return HttpResponse("FILE NOT FOUND", content_type="text/html")



def getFileCroppedResized(request, height,width):
     allow_access = True
     #file_record = models.Campground.objects.get(id=file_id)
     mediafile = request=request.GET.get('mediafile',None)
     mediafile = mediafile.replace(settings.MEDIA_URL, '')
     BASE_DIR = settings.BASE_DIR

     local_file = settings.MEDIA_ROOT+'/'+mediafile
     file_name_path = local_file
     extension=mediafile[-3:]
     if os.path.isfile(file_name_path) is True:
             reszie_file_name = file_name_path[:len(file_name_path)-4]
             reszie_file_name_extension = file_name_path[-4:]
             reszie_fn = reszie_file_name+'-cropped-'+height+'x'+width+reszie_file_name_extension
             if os.path.isfile(reszie_fn) is False:
                 img = Image.open(file_name_path)
                 img = img.resize((int(width), int(height)), Image.Resampling.LANCZOS)
                 img = crop_max_square(img)
                 img.save(reszie_fn)

             the_file = open(reszie_fn, 'rb')
             the_data = the_file.read()
             the_file.close()
             if extension == 'msg':
                 return HttpResponse(the_data, content_type="application/vnd.ms-outlook")
             if extension == 'eml':
                 return HttpResponse(the_data, content_type="application/vnd.ms-outlook")

             return HttpResponse(the_data, content_type=mimetypes.types_map['.'+str(extension)])
     else:
         reszie_fn = BASE_DIR+"/parkstay/static/ps/img/no_image.jpg"
         extension = 'jpg'
         the_file = open(reszie_fn, 'rb')
         the_data = the_file.read()
         the_file.close()
         return HttpResponse(the_data, content_type=mimetypes.types_map['.'+str(extension)])


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def crop_max_square(pil_img):
      return crop_center(pil_img, min(pil_img.size), min(pil_img.size))
