from flask import Blueprint, request, render_template, redirect
from .model import YOLOModel
import os

views = Blueprint('views', __name__)
yolov10 = YOLOModel()

@views.route('/')
def index():
    for file in os.listdir('GUI/static/predictions'):
        os.remove(f'GUI/static/predictions/{file}')
    return render_template('home.html', current_page='home')

@views.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'GET':
        return redirect('/')
    elif request.method == 'POST':
      # clear the uploads folder
      for file in os.listdir('uploads'):
            os.remove(f'uploads/{file}')

      # save the uploaded files
      file_dict = request.files.to_dict(flat=False)
      file_names = {'images': [], 'videos': []}
      invalid_files = []
      for i, file in enumerate(file_dict['files']):
            # print(file.filename) # Screenshot 2024-05-23 215851.png
            # print(file.content_type) # image/png | video/mp4
            # print(file.stream) # <tempfile.SpooledTemporaryFile object at 0x000001CF06883700>
            # print(file.headers) # Content-Disposition: form-data; name="files"; filename="Screenshot 2024-05-23 215851.png", Content-Type: image/png
            # print(file.mimetype) # image/png | video/mp4
            file_content = file.stream.read()
            if file.content_type.startswith('image'):
                  # from binary to n
                  with open(f'uploads/image_{i:02d}.jpg', 'wb') as f:
                        f.write(file_content)
                        file_names['images'].append(f.name)
            elif file.content_type.startswith('video'):
                  with open(f'uploads/video_{i:02d}.mp4', 'wb') as f:
                        f.write(file_content)
                        file_names['videos'].append(f.name)
            else:
                  invalid_files.append(file.filename)

      print(f'{len(file_names["images"])} images and {len(file_names["videos"])} videos have been uploaded')
      
      if len(invalid_files) == 0:
        paths, is_val = predict(file_names)
        paths = paths['images'] + paths['videos']
        paths.sort(key=lambda x: x.split('_')[-1].split('.')[0])
        obj = {'status': 'success', 
                'paths': paths, 
                'is_full_view': len(paths) == 1,
                'message': 'The files have been uploaded and predicted successfully'} if is_val else {'status': 'error', 'message': 'No objects have been detected in the uploaded files'}
      else:
        obj = {'status': 'error', 'message': f'The following files are invalid: {", ".join(invalid_files)}, please upload only images or/and videos.'}

      return render_template('home.html', **obj, current_page='home')

def predict(file_names):
    stored_paths = {'images': [], 'videos': []}
    for path2img in file_names['images']:
      stored_path, is_val = yolov10.process(path2img, f'GUI/static/predictions/{os.path.basename(path2img)}')
      stored_paths['images'].append(stored_path)
    for path2vid in file_names['videos']:
      stored_path, is_val = yolov10.process(path2vid, f'GUI/static/predictions/{os.path.basename(path2vid)}')
      stored_paths['videos'].append(stored_path)

    return stored_paths, is_val

@views.route('/about')
def about():
    return render_template('about.html', current_page='about')

@views.route('/contact')
def contact():
    return render_template('contact.html', current_page='contact')