import uuid
import base64
import binascii
from django.core.files.base import ContentFile


def get_file_extension(file_name, decoded_file):
    import imghdr

    extension = imghdr.what(file_name, decoded_file)
    extension = "jpg" if extension == "jpeg" else extension
    return extension

def strip_b64_header(content):
    if ';base64,' in content:
        header, base64_data = content.split(';base64,')
        return base64_data
    return content

def get_image_content_file(content):
    base64_data = strip_b64_header(content)
    try:
        decoded_file = base64.b64decode(base64_data)
    except (TypeError, binascii.Error):
        raise Exception("Invalid File Exception")
    file_name = str(uuid.uuid4())[:12]
    file_extension = get_file_extension(file_name, decoded_file)
    complete_file_name = "{}.{}".format(file_name, file_extension)
    image_content_file = ContentFile(decoded_file, name=complete_file_name)
    return image_content_file
