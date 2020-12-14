from . import passport
from app1.utils.captcha.captcha import captcha
from app1 import redis_store
from flask import request, current_app, make_response
from app1 import constants

@passport.route('/image_code')
def image_code():
    print(request.url)
    cur_id = request.args.get('cur_id')
    pre_id = request.args.get('pre_id')
    print(cur_id)
    name, text, image_data = captcha.generate_captcha()
    try:
        redis_store.set('img_code:%s'%cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
        if pre_id:
            redis_store.delete('img_code:%s' % pre_id)
    except Exception as e:
        current_app.logger.error(e)

    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'
    return response