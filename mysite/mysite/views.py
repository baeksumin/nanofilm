from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import subprocess
import os
import glob
import cv2


@csrf_exempt  # Used for CSRF protection on POST requests
def take(request):
    if request.method == 'POST':
        result = {}
        try:
            # Check and create the image storage folder
            folder_path = '/jetson_image'
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            file_name = f"{folder_path}/image_"
            subprocess.run(["nvgstcapture-1.0", "--automate", "--capture-auto", "--file-name", file_name], check=True)

            file_list = glob.glob(f"{file_name}_*.jpg")
            latest_file = max(file_list, key=os.path.getctime)
            ab_path = os.path.abspath(latest_file)

            result['status'] = 'success'
            result['captured_photo'] = ab_path

        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)

        return JsonResponse(result)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def composite(request):
    background_paths = [
        './mysite/template/background_image1.jpg',
        './mysite/template/background_image2.jpg',
        './mysite/template/background_image3.jpg',
        './mysite/template/background_image4.jpg',
    ]

    image_path = request.GET.get('image_path')
    result = {}

    try:
        composite_image_paths = []
        y_offset = 50
        top_crop = 45
        bottom_crop = 40

        for i, background_path in enumerate(background_paths, start=1):
            background_image = cv2.imread(background_path)
            image = cv2.imread(image_path)

            image = cv2.resize(image, (int(background_image.shape[1] / 1.13), int(background_image.shape[0] / 1.13)))
            image = image[top_crop:-bottom_crop, :]
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray_image = cv2.merge([gray_image, gray_image, gray_image])

            x = (background_image.shape[1] - gray_image.shape[1]) // 2
            y = (background_image.shape[0] - gray_image.shape[0]) // 2 + y_offset

            merged_image = background_image.copy()
            merged_image[y:y + gray_image.shape[0], x:x + gray_image.shape[1]] = gray_image

            output_path = f'./mysite/result/output_image_combined_{i}.jpg'
            cv2.imwrite(output_path, merged_image)
            ab_path = os.path.abspath(output_path)
            composite_image_paths.append(ab_path)

        result['status'] = 'success'
        result['composite_images'] = composite_image_paths

    except Exception as e:
        result['status'] = 'error'
        result['message'] = str(e)

    return JsonResponse(result)
